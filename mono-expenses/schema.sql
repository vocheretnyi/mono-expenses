-- NOTES:
-- "balance" column was removed from the schema, while it was present in the JSON file.
-- column "time" was changed to store DATETIME instead of INT (Unix time format).
-- monetary columns were changed to DECIMAL(15, 2) to store amounts in the hryvnias instead of kopecks.

CREATE TABLE Transactions (
    id VARCHAR(255) PRIMARY KEY COMMENT 'Unique transaction ID',
    time DATETIME COMMENT 'Transaction time in seconds in Unix time format',
    description TEXT COMMENT 'Description of the transaction',
    mcc INT COMMENT 'Transaction type code (Merchant Category Code), according to ISO 18245',
    originalMcc INT COMMENT 'Original transaction type code (Merchant Category Code), according to ISO 18245',
    hold BOOLEAN COMMENT 'Status of amount hold',
    amount DECIMAL(15, 2) COMMENT 'Amount in the account currency in the smallest units (cents, kopecks)',
    operationAmount DECIMAL(15, 2) COMMENT 'Amount in the transaction currency in the smallest units (cents, kopecks)',
    currencyCode INT COMMENT 'Account currency code according to ISO 4217',
    commissionRate DECIMAL(15, 2) COMMENT 'Commission amount in the smallest units (cents, kopecks)',
    cashbackAmount DECIMAL(15, 2) COMMENT 'Cashback amount in the smallest units (cents, kopecks)',
    comment TEXT COMMENT 'Comment on the transfer entered by the user. If not specified, the field will be absent' DEFAULT NULL,
    receiptId VARCHAR(255) COMMENT 'Receipt number for check.gov.ua. The field may be absent' DEFAULT NULL,
    invoiceId VARCHAR(255) COMMENT 'Invoice number for private entrepreneurs, appears if it is a credit operation' DEFAULT NULL,
    counterEdrpou VARCHAR(255) COMMENT 'EDRPOU of the counterparty, present only for private entrepreneur account statements' DEFAULT NULL,
    counterIban VARCHAR(255) COMMENT 'IBAN of the counterparty, present only for private entrepreneur account statements' DEFAULT NULL,
    counterName VARCHAR(255) COMMENT 'Name of the counterparty' DEFAULT NULL
);