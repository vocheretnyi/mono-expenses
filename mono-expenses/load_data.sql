
LOAD DATA LOCAL INFILE 'statements.json'
INTO TABLE Transactions
FORMAT JSON
(
    id <- id,
    @time <- time,
    description <- description,
    mcc <- mcc,
    originalMcc <- originalMcc,
    hold <- hold,
    @amount <- amount,
    @operationAmount <- operationAmount,
    currencyCode <- currencyCode,
    @commissionRate <- commissionRate,
    @cashbackAmount <- cashbackAmount,
    comment <- comment DEFAULT NULL,
    receiptId <- receiptId DEFAULT NULL,
    invoiceId <- invoiceId DEFAULT NULL,
    counterEdrpou <- counterEdrpou DEFAULT NULL,
    counterIban <- counterIban DEFAULT NULL,
    counterName <- counterName DEFAULT NULL
)
SET
    time = CONVERT_TZ(FROM_UNIXTIME(@time), 'GMT', '+03:00'),
    amount = @amount / 100,
    operationAmount = @operationAmount / 100,
    commissionRate = @commissionRate / 100,
    cashbackAmount = @cashbackAmount / 100;

