from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.http import HttpResponse

from game.service.start_hand import start_hand

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Setup minimal session data required by many views
        session = self.client.session
        session['hand_ids'] = [1]
        session['hand_index'] = 0
        session.save()

    @patch('game.views.start_hand')
    def test_start_hand_view_calls_service(self, mock_start):
        mock_start.return_value = HttpResponse(status=200)
        response = self.client.get(reverse('game:start_hand'))
        self.assertTrue(mock_start.called)
        self.assertEqual(response.status_code, 200)

    @patch('game.views.reset_chip_stack')
    def test_reset_chips_view_calls_service(self, mock_reset):
        mock_reset.return_value = HttpResponse(status=200)
        response = self.client.post(reverse('game:reset_chips'))
        self.assertTrue(mock_reset.called)
        self.assertEqual(response.status_code, 200)

    @patch('game.views.play_hand')
    def test_play_hand_view_calls_service(self, mock_play):
        mock_play.return_value = HttpResponse(status=200)
        response = self.client.get(reverse('game:play_hand'))
        self.assertTrue(mock_play.called)
        self.assertEqual(response.status_code, 200)

    @patch('game.views.double')
    def test_double_view_calls_service(self, mock_double):
        mock_double.return_value = HttpResponse(status=200)
        response = self.client.post(reverse('game:double'))
        self.assertTrue(mock_double.called)
        self.assertEqual(response.status_code, 200)

    @patch('game.views.split')
    def test_split_view_calls_service(self, mock_split):
        mock_split.return_value = HttpResponse(status=200)
        response = self.client.post(reverse('game:split'))
        self.assertTrue(mock_split.called)
        self.assertEqual(response.status_code, 200)

    @patch('game.views.insurance')
    def test_insurance_view_calls_service(self, mock_insurance):
        mock_insurance.return_value = HttpResponse(status=200)
        response = self.client.post(reverse('game:insurance'))
        self.assertTrue(mock_insurance.called)
        self.assertEqual(response.status_code, 200)

    @patch('game.views.even_money')
    def test_even_money_view_calls_service(self, mock_even_money):
        mock_even_money.return_value = HttpResponse(status=200)
        response = self.client.post(reverse('game:even_money'))
        self.assertTrue(mock_even_money.called)
        self.assertEqual(response.status_code, 200)

    @patch('game.views.hit')
    def test_hit_view_calls_service(self, mock_hit):
        mock_hit.return_value = HttpResponse(status=200)
        response = self.client.post(reverse('game:hit'))
        self.assertTrue(mock_hit.called)
        self.assertEqual(response.status_code, 200)
