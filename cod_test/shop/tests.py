from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta
import json
from django.core.files.uploadedfile import SimpleUploadedFile

from customer.models import Customer, Panier, ProduitPanier, Commande
from shop.models import CategorieEtablissement, CategorieProduit, Etablissement, Produit


def _make_etablissement_with_product_owner(user):
    # S'assurer que les champs requis de l'utilisateur sont définis pour éviter les erreurs de contrainte NOT NULL
    user.first_name = "SellerFirst"
    user.last_name = "SellerLast"
    user.email = "seller@example.com"
    user.save(update_fields=["first_name", "last_name", "email"])

    cat_etab = CategorieEtablissement.objects.create(nom="CatE", description="d")
    cat_prod = CategorieProduit.objects.create(nom="CatP", description="d", categorie=cat_etab)

    logo = SimpleUploadedFile("logo.jpg", b"x", content_type="image/jpeg")
    couverture = SimpleUploadedFile("cover.jpg", b"y", content_type="image/jpeg")

    etab = Etablissement.objects.create(
        user=user,
        nom="Etab",
        description="d",
        logo=logo,
        couverture=couverture,
        categorie=cat_etab,
        adresse="addr",
        pays="CI",
        contact_1="01020304",
        email="etab@example.com",
        nom_du_responsable="SellerLast",
        prenoms_duresponsable="SellerFirst",
    )
    return etab, cat_prod


class ShopPaiementDetailsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_paiement_details_creates_commande_and_moves_cart_items(self):
        user = User.objects.create_user(username="buyer", password="pass", email="buyer@example.com")
        customer = Customer.objects.create(user=user, adresse="addr", contact_1="01020304")

        panier = Panier.objects.create(customer=customer)

        etab_user = User.objects.create_user(username="seller", password="pass", email="seller@example.com")
        etab, cat_prod = _make_etablissement_with_product_owner(etab_user)

        produit = Produit.objects.create(
            nom="P",
            description="d",
            description_deal="dd",
            prix=100,
            prix_promotionnel=80,
            categorie=cat_prod,
            etablissement=etab,
            date_debut_promo=(now().date() - timedelta(days=1)),
            date_fin_promo=(now().date() + timedelta(days=1)),
        )
        line = ProduitPanier.objects.create(produit=produit, panier=panier, quantite=2)

        self.client.login(username="buyer", password="pass")

        url = reverse("paiement_detail")
        payload = {
            "transaction_id": "trx123",
            "notify_url": "http://example.com/notify",
            "return_url": "http://example.com/return",
            "panier": panier.id,
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type="application/json")

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["success"])

        commande = Commande.objects.get(customer=customer, transaction_id="trx123")
        # À ce stade, le panier a été supprimé ; comparer avec le total attendu à la place
        self.assertEqual(commande.prix_total, 160.0)

        line.refresh_from_db()
        self.assertIsNone(line.panier)
        self.assertEqual(line.commande_id, commande.id)

        self.assertFalse(Panier.objects.filter(id=panier.id).exists())

    def test_post_paiement_details_fails_when_panier_not_owned(self):
        user = User.objects.create_user(username="buyer2", password="pass", email="buyer2@example.com")
        Customer.objects.create(user=user, adresse="addr", contact_1="01020304")

        other_user = User.objects.create_user(username="other", password="pass", email="other@example.com")
        other_customer = Customer.objects.create(user=other_user, adresse="addr", contact_1="01020304")
        panier = Panier.objects.create(customer=other_customer)

        self.client.login(username="buyer2", password="pass")

        url = reverse("paiement_detail")
        payload = {
            "transaction_id": "trx999",
            "notify_url": "http://example.com/notify",
            "return_url": "http://example.com/return",
            "panier": panier.id,
        }
        resp = self.client.post(url, data=json.dumps(payload), content_type="application/json")

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data["success"])


class ShopViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="shopuser", password="pass")
        self.customer = Customer.objects.create(user=self.user)
        
        self.etab_user = User.objects.create_user(username="seller", password="pass")
        self.etab, self.cat_prod = _make_etablissement_with_product_owner(self.etab_user)
        
        self.produit = Produit.objects.create(
            nom="ShopProd", description="d", prix=100, 
            categorie=self.cat_prod, etablissement=self.etab, status=True, slug="shop-prod"
        )

    def test_shop_view_loads(self):
        url = reverse("shop")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("produits", resp.context)

    def test_product_detail_view_loads_and_context(self):
        url = reverse("product_detail", args=[self.produit.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["produit"], self.produit)

    def test_toggle_favorite_anonymous_redirects(self):
        url = reverse("toggle_favorite", args=[self.produit.id])
        resp = self.client.get(url)
        self.assertRedirects(resp, reverse("login"))

    def test_toggle_favorite_authenticated_adds_and_removes(self):
        self.client.force_login(self.user)
        url = reverse("toggle_favorite", args=[self.produit.id])
        
        # Add
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.user.favorite_set.filter(produit=self.produit).exists())
        
        # Remove
        resp = self.client.get(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(self.user.favorite_set.filter(produit=self.produit).exists())

    def test_single_view_by_category_slug(self):
        # Le slug pour la catégorie vient du nom ? La logique semble attendre un champ slug 
        # CategorieProduit a généralement un champ slug.
        # Nous devons définir le slug manuellement si nous ne vérifions pas la méthode save du modèle.
        self.cat_prod.slug = "cat-slug"
        self.cat_prod.save()
        
        url = reverse("single", args=["cat-slug"])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("produits", resp.context)


class ShopDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Seller with establishment
        self.seller = User.objects.create_user(username="dashboard_seller", password="pass")
        self.etab, self.cat_prod = _make_etablissement_with_product_owner(self.seller)
        
        # Buyer
        self.buyer = User.objects.create_user(username="buyer_dash", password="pass")
        
    def test_dashboard_access_denied_anonymous(self):
        url = reverse("dashboard")
        resp = self.client.get(url)
        self.assertRedirects(resp, reverse("login") + "?next=" + url)

    def test_dashboard_access_allowed_seller(self):
        self.client.force_login(self.seller)
        url = reverse("dashboard")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
    def test_ajout_article(self):
        self.client.force_login(self.seller)
        url = reverse("ajout_article")
        
        # PRODUCTION D'UNE IMAGE VALIDE
        img = SimpleUploadedFile("prod.jpg", b"content", content_type="image/jpeg")
        
        data = {
            "nom": "New Prod", "description": "Desc", "prix": "500", 
            "quantite": "10", "categorie": self.cat_prod.id,
            "image": img
        }
        # View uses request.FILES.get('image'), expect it to work.
        # Ensuring category exists (it does from setUp).
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Produit.objects.filter(nom="New Prod").exists())

    def test_modifier_article(self):
        self.client.force_login(self.seller)
        prod = Produit.objects.create(
            nom="Old Name", description="d", prix=100, 
            categorie=self.cat_prod, etablissement=self.etab
        )
        url = reverse("modifier", args=[prod.id])
        
        data = {
            "nom": "New Name", "description": "d", "prix": "200", 
            "quantite": "5", "categorie": self.cat_prod.id
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        prod.refresh_from_db()
        self.assertEqual(prod.nom, "New Name")
        self.assertEqual(prod.prix, 200)

    def test_supprimer_article(self):
        self.client.force_login(self.seller)
        prod = Produit.objects.create(
            nom="To Delete", description="d", prix=100, 
            categorie=self.cat_prod, etablissement=self.etab
        )
        url = reverse("supprimer_article", args=[prod.id])
        # La vue nécessite une méthode POST
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Produit.objects.filter(id=prod.id).exists())
        
    def test_commande_recu_permissions_and_filters(self):
        self.client.force_login(self.seller)
        url = reverse("commande-reçu")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
        resp_filter = self.client.get(url, {"status": "attente"})
        self.assertEqual(resp_filter.status_code, 200)
