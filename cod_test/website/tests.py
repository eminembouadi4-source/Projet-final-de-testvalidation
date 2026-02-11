from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware

from customer.models import Customer, Panier
from website import context_processors, models
from website.models import SiteInfo, Galerie, Horaire
from shop.models import CategorieEtablissement
from unittest.mock import patch, MagicMock

# Create your tests here.


def _add_session_to_request(request):
    middleware = SessionMiddleware(lambda _req: None)
    middleware.process_request(request)
    request.session.save()
    return request


class WebsiteContextProcessorsTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    # --- SiteInfo Tests ---
    def test_site_infos_returns_none_when_no_siteinfo(self):
        request = self.factory.get("/")
        ctx = context_processors.site_infos(request)
        self.assertIn("infos", ctx)
        self.assertIsNone(ctx["infos"])

    def test_site_infos_returns_latest_siteinfo(self):
        SiteInfo.objects.create(
            titre="t1",
            slogan="s",
            description="d",
            horaire_description="h",
            text_pourquoi_nous_choisir="p",
            arriere_plan_appreciation="a.jpg",
            image_session_pourquoi_nous_choisir="b.jpg",
            image_page_contact="c.jpg",
            contact_1="01020304",
            contact_2="05060708",
            email="a@a.com",
            adresse="addr",
            map_url="http://example.com",
            facebook_url="http://example.com",
            instagram_url="http://example.com",
            twitter_url="http://example.com",
            whatsapp="wa",
        )
        latest = SiteInfo.objects.create(
            titre="t2",
            slogan="s",
            description="d",
            horaire_description="h",
            text_pourquoi_nous_choisir="p",
            arriere_plan_appreciation="a.jpg",
            image_session_pourquoi_nous_choisir="b.jpg",
            image_page_contact="c.jpg",
            contact_1="01020304",
            contact_2="05060708",
            email="b@b.com",
            adresse="addr",
            map_url="http://example.com",
            facebook_url="http://example.com",
            instagram_url="http://example.com",
            twitter_url="http://example.com",
            whatsapp="wa",
        )
        request = self.factory.get("/")
        ctx = context_processors.site_infos(request)
        self.assertEqual(ctx["infos"].id, latest.id)

    # --- Categories Tests ---
    def test_categories_returns_only_active_categories(self):
        CategorieEtablissement.objects.create(nom="Active", description="d", status=True)
        CategorieEtablissement.objects.create(nom="Inactive", description="d", status=False)
        
        request = self.factory.get("/")
        ctx = context_processors.categories(request)
        
        self.assertIn("cat", ctx)
        self.assertEqual(ctx["cat"].count(), 1)
        self.assertEqual(ctx["cat"].first().nom, "Active")

    def test_categories_returns_empty_when_none_active(self):
        CategorieEtablissement.objects.create(nom="Inactive", description="d", status=False)
        
        request = self.factory.get("/")
        ctx = context_processors.categories(request)
        
        self.assertEqual(ctx["cat"].count(), 0)

    # --- Galeries Tests ---
    def test_galeries_returns_max_6_items(self):
        for i in range(10):
            Galerie.objects.create(titre=f"G{i}", image="img.jpg", status=True)
        
        request = self.factory.get("/")
        ctx = context_processors.galeries(request)
        
        self.assertIn("galeries", ctx)
        self.assertEqual(len(ctx["galeries"]), 6)

    def test_galeries_returns_only_active(self):
        Galerie.objects.create(titre="Active", image="img.jpg", status=True)
        Galerie.objects.create(titre="Inactive", image="img.jpg", status=False)
        
        request = self.factory.get("/")
        ctx = context_processors.galeries(request)
        
        self.assertEqual(len(ctx["galeries"]), 1)

    # --- Horaires Tests ---
    def test_horaires_returns_only_active(self):
        Horaire.objects.create(titre="Lundi", description="9h-17h", status=True)
        Horaire.objects.create(titre="Fermé", description="N/A", status=False)
        
        request = self.factory.get("/")
        ctx = context_processors.horaires(request)
        
        self.assertIn("horaires", ctx)
        self.assertEqual(ctx["horaires"].count(), 1)

    # --- Cart Tests ---
    def test_cart_context_processor_creates_cart_for_anonymous(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        _add_session_to_request(request)

        ctx = context_processors.cart(request)
        self.assertIn("cart", ctx)
        self.assertIsInstance(ctx["cart"], Panier)
        self.assertIsNotNone(ctx["cart"].id)

    def test_cart_context_processor_creates_cart_for_authenticated_user(self):
        user = User.objects.create_user(username="u1", password="pass")
        Customer.objects.create(user=user, adresse="addr", contact_1="01020304")

        request = self.factory.get("/")
        request.user = user
        _add_session_to_request(request)

        ctx = context_processors.cart(request)
        self.assertIn("cart", ctx)
        self.assertIsInstance(ctx["cart"], Panier)
        self.assertEqual(ctx["cart"].customer.user_id, user.id)

    def test_cart_context_processor_handles_exception_gracefully(self):
        """Tester que le processeur de panier retourne une chaîne vide en cas d'exception (comportement actuel)"""
        request = self.factory.get("/")
        request.user = AnonymousUser()
        # Ne pas ajouter de session - cela causera une exception
        
        ctx = context_processors.cart(request)
        self.assertIn("cart", ctx)
        # L'implémentation actuelle retourne "" en cas d'exception
        self.assertEqual(ctx["cart"], "")

    # --- Cities Tests ---
    @patch("website.context_processors.City")
    def test_cities_returns_all_cities(self, mock_city):
        mock_city.objects.all.return_value = ["Abidjan", "Bouaké"]
        
        request = self.factory.get("/")
        ctx = context_processors.cities(request)
        
        self.assertIn("cities", ctx)
        self.assertEqual(ctx["cities"], ["Abidjan", "Bouaké"])


class WebsiteModelsTests(TestCase):
    def test_site_info_str(self):
        site_info = SiteInfo.objects.create(titre="My Site", slogan="s", description="d")
        self.assertEqual(str(site_info), "My Site")

    def test_banniere_creation_optional_image(self):
        banniere = models.Banniere.objects.create(titre="Banner", description="Desc")
        self.assertIsNone(banniere.couverture.name)
        self.assertEqual(str(banniere), "Banner")


