from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from customer.models import Customer, Commande, Panier, ProduitPanier
from shop.models import CategorieEtablissement, CategorieProduit, Etablissement, Produit
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from website.models import SiteInfo

def _make_etablissement(user):
    user.save()
    cat_etab = CategorieEtablissement.objects.create(nom="CatE", description="d")
    cat_prod = CategorieProduit.objects.create(nom="CatP", description="d", categorie=cat_etab)
    etab = Etablissement.objects.create(
        user=user, nom="Etab", description="d", categorie=cat_etab,
        adresse="addr", pays="CI", contact_1="01020304", email="etab@example.com"
    )
    return etab, cat_prod

class ClientViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="client1", password="pass", email="cl@cl.com")
        self.customer = Customer.objects.create(user=self.user, contact_1="0000", adresse="home")
        
        # Initialisation pour les commandes
        self.seller = User.objects.create_user(username="seller_cl", password="pass")
        self.etab, self.cat_prod = _make_etablissement(self.seller)
        self.produit = Produit.objects.create(
            nom="Prod1", description="d", prix=100, 
            categorie=self.cat_prod, etablissement=self.etab
        )
        self.commande = Commande.objects.create(
            customer=self.customer, transaction_id="TRX001", prix_total=100
        )
        ProduitPanier.objects.create(commande=self.commande, produit=self.produit, quantite=1)

    # --- Tests de Contrôle d'Accès & Redirection ---
    def test_views_redirect_anonymous(self):
        views = [
            "profil", "commande", "suivie-commande", "souhait", "avis", "evaluation", "parametre"
        ]
        for v in views:
            resp = self.client.get(reverse(v))
            self.assertRedirects(resp, reverse("login") + "?next=" + reverse(v))

    def test_views_redirect_user_without_customer_profile(self):
        no_cust_user = User.objects.create_user(username="no_cust", password="p")
        self.client.force_login(no_cust_user)
        
        views = ["profil", "commande", "suivie-commande", "souhait", "avis", "evaluation", "parametre"]
        for v in views:
            resp = self.client.get(reverse(v), follow=True)
            # Les vues redirigent vers 'index' si le client est manquant
            self.assertRedirects(resp, reverse("index"))

    # --- Tests Nominaux ---
    def test_profil_loads_and_shows_commands(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("profil"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("dernieres_commandes", resp.context)
        self.assertEqual(list(resp.context["dernieres_commandes"]), [self.commande])

    def test_commande_view_list_and_search(self):
        self.client.force_login(self.user)
        url = reverse("commande")
        
        # Liste
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("commandes_paginated", resp.context)
        
        # Recherche
        resp_search = self.client.get(url, {"q": "TRX001"})
        self.assertEqual(resp_search.status_code, 200)
        self.assertEqual(len(resp_search.context["commandes_paginated"]), 1)
        
        # Recherche non trouvée
        resp_none = self.client.get(url, {"q": "NOTFOUND"})
        self.assertEqual(len(resp_none.context["commandes_paginated"]), 0)

    def test_commande_detail_view(self):
        self.client.force_login(self.user)
        url = reverse("commande-detail", args=[self.commande.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["commande"], self.commande)

    def test_parametre_update(self):
        self.client.force_login(self.user)
        url = reverse("parametre")
        
        # GET
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        
        # POST - mise à jour des infos
        data = {
            "first_name": "NewFirst", "last_name": "NewLast",
            "contact": "9999", "address": "New Addr"
        }
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        
        self.user.refresh_from_db()
        self.customer.refresh_from_db()
        self.assertEqual(self.user.first_name, "NewFirst")
        self.assertEqual(self.customer.contact_1, "9999")

    # --- Test Facture PDF (Mocké) ---
    @patch("client.views.sync_playwright")
    @patch("client.views.SiteInfo")
    @patch("client.views.qrcode_base64")
    def test_invoice_pdf_generation(self, mock_qr, mock_siteinfo, mock_playwright):
        self.client.force_login(self.user)
        
        # Mock SiteInfo
        mock_site = MagicMock()
        mock_site.logo.url = "/media/logo.png"
        mock_siteinfo.objects.latest.return_value = mock_site
        
        # Mock Playwright
        mock_p = MagicMock()
        mock_browser = MagicMock()
        mock_page = MagicMock()
        
        mock_playwright.return_value.__enter__.return_value = mock_p
        mock_p.chromium.launch.return_value = mock_browser
        mock_browser.new_page.return_value = mock_page
        mock_page.pdf.return_value = b"%PDF-1.4..." # Fake PDF bytes
        
        url = reverse("invoice_pdf", args=[self.commande.id])
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "application/pdf")
        self.assertIn(f"Recu_{self.commande.transaction_id}.pdf", resp["Content-Disposition"])

    def test_invoice_pdf_security_check(self):
        # Accéder à la facture d'un autre utilisateur
        other_user = User.objects.create_user(username="other", password="p")
        other_customer = Customer.objects.create(user=other_user)
        other_order = Commande.objects.create(customer=other_customer, transaction_id="TRX999")
        
        self.client.force_login(self.user) # Login as user1
        url = reverse("invoice_pdf", args=[other_order.id])
        resp = self.client.get(url, follow=True)
        
        # Devrait rediriger vers la liste 'commande'
        self.assertRedirects(resp, reverse("commande"))
