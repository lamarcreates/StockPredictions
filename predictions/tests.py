import datetime
from unittest.mock import patch

import pandas as pd
from django.test import SimpleTestCase
from django.urls import reverse

from .views import StockForm


class StockPageTests(SimpleTestCase):
    def test_home_page_renders(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Stock Prediction')
        self.assertContains(response, 'name="stock_name"')

    @patch('predictions.views.now')
    def test_home_page_is_open_during_weekday_hours(self, mock_now):
        mock_now.return_value = datetime.datetime(2020, 6, 22, 12, 0)

        response = self.client.get(reverse('home'))

        self.assertIs(response.context['open'], True)
        self.assertContains(response, 'We are currently open!')

    @patch('predictions.views.now')
    def test_home_page_is_closed_on_weekends(self, mock_now):
        mock_now.return_value = datetime.datetime(2020, 6, 21, 12, 0)

        response = self.client.get(reverse('home'))

        self.assertIs(response.context['open'], False)
        self.assertContains(response, 'We are currently closed!')

    @patch('predictions.views.web.DataReader')
    def test_stock_submission_renders_without_image_dependencies(self, mock_reader):
        mock_reader.return_value = pd.DataFrame({'Close': [100.0]})

        response = self.client.post(reverse('home'), {'stock_name': 'AAPL'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        mock_reader.assert_called_once_with(
            'AAPL', 'yahoo', datetime.datetime(2010, 1, 1),
            datetime.datetime(2019, 1, 11),
        )

    def test_stock_form_accepts_a_symbol(self):
        form = StockForm({'stock_name': 'AAPL'})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['stock_name'], 'AAPL')
