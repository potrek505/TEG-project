ALL_TRANSACTIONS_TABLE_STRUCTURE = """
1. id - INTEGER (primary key)
2. account_id - TEXT - account identifier
3. transaction_id - TEXT - unique transaction ID
4. internal_transaction_id - TEXT - internal transaction ID
5. booking_date - TEXT - booking date (format: YYYY-MM-DD)
6. value_date - TEXT - value date (format: YYYY-MM-DD)
7. booking_date_time - TEXT - full date and time (ISO 8601)
8. amount - REAL - transaction amount (negative = expense, positive = income)
9. currency - TEXT - currency (e.g., 'PLN')
10. remittance_info_unstructured - TEXT - transaction description
11. remittance_info_array - TEXT - description as JSON array
12. creditor_name - TEXT - creditor name
13. creditor_iban - TEXT - creditor IBAN
14. debtor_name - TEXT - debtor name
15. debtor_iban - TEXT - debtor IBAN
16. balance_after_amount - REAL - balance after transaction
17. balance_after_currency - TEXT - balance currency
18. balance_after_type - TEXT - balance type (e.g., 'interimBooked')
19. raw_data - TEXT - full transaction data as JSON
"""