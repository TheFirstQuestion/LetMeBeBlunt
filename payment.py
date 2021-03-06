import imp
import os
import sys
import decimal

from authorizenet import apicontractsv1
from authorizenet.apicontrollers import createTransactionController
import app


CONSTANTS = imp.load_source('modulename', 'constants.py')
FORM_INFO = {}
TOTAL = 0

def doThePayStuff(formStuff):
    # Clear from previous purchases
    global TOTAL
    TOTAL = 0
    global FORM_INFO
    FORM_INFO = {}
    for i in formStuff:
        if i == "FormStuff":
            parseDict(formStuff[i])
        else:
            FORM_INFO.update({i: formStuff[i]})
    print(FORM_INFO)
    for i in FORM_INFO["Purchases"]:
        TOTAL = TOTAL + (int(i[1]) * decimal.Decimal(i[2]))
    charge_credit_card()


def parseDict(inp):
    purchases = []
    inp = inp[20:].split(")")
    for x in inp:
        terms = x.split(",")
        #print(terms)
        if len(terms) < 2:
            continue
        #print("Total" in terms[0])
        if "Total" in terms[0]:
            #global TOTAL
            TOTAL = terms[1][3:8]
        elif "Total" in terms[1]:
            #global TOTAL
            TOTAL = terms[2][3:8]
        else:
            if len(terms) == 2:
                name = terms[0][2:-5]
                qty = terms[1][2:-1]
            else:
                name = terms[1][3:-5]
                qty = terms[2][2:-1]
            #print(name)
            p = app.getProduct(name)[0]
            price = p["Price"][-12:-7]
            purchases.append([name, qty, price])
    FORM_INFO.update({"Purchases": purchases})


# From https://github.com/AuthorizeNet/sample-code-python
def charge_credit_card():
    # Create a merchantAuthenticationType object with authentication details retrieved from the constants file
    merchantAuth = apicontractsv1.merchantAuthenticationType()
    merchantAuth.name = CONSTANTS.apiLoginId
    merchantAuth.transactionKey = CONSTANTS.transactionKey

    # Create the payment data for a credit card
    creditCard = apicontractsv1.creditCardType()
    creditCard.cardNumber = FORM_INFO["Number"]
    creditCard.expirationDate = FORM_INFO["Year"] + "-" + FORM_INFO["Month"]
    creditCard.cardCode = FORM_INFO["CVV"]

    # Add the payment data to a paymentType object
    payment = apicontractsv1.paymentType()
    payment.creditCard = creditCard

    # Create order information
    order = apicontractsv1.orderType()
    #order.invoiceNumber = "10101"
    order.description = "Product order"

    # Set the customer's Bill To address
    customerAddress = apicontractsv1.customerAddressType()
    name = FORM_INFO["Name"].split(" ")
    customerAddress.firstName = name[0]
    customerAddress.lastName = name[1]
    #customerAddress.company = "Souveniropolis"
    customerAddress.address = FORM_INFO["Address"]
    customerAddress.city = "Indianapolis"
    customerAddress.state = "IN"
    customerAddress.zip = FORM_INFO["ZipCode"]
    customerAddress.country = "USA"
    customerAddress.phoneNumber = FORM_INFO["Phone"]

    # Set the customer's identifying information
    customerData = apicontractsv1.customerDataType()
    customerData.type = "individual"
    #customerData.id = "99999456654"
    customerData.email = FORM_INFO["Email"]

    # Add values for transaction settings
    duplicateWindowSetting = apicontractsv1.settingType()
    duplicateWindowSetting.settingName = "duplicateWindow"
    duplicateWindowSetting.settingValue = "600"
    settings = apicontractsv1.ArrayOfSetting()
    settings.setting.append(duplicateWindowSetting)

    # build the array of line items
    line_items = apicontractsv1.ArrayOfLineItem()
    for i in FORM_INFO["Purchases"]:
        # setup individual line items
        line_item_1 = apicontractsv1.lineItemType()
        line_item_1.itemId = i[0]
        line_item_1.name = i[0]
        #line_item_1.description = str(PRODUCT[4])
        line_item_1.quantity = i[1]
        line_item_1.unitPrice = i[2]

        line_items.lineItem.append(line_item_1)

    # Create a transactionRequestType object and add the previous objects to it.
    transactionrequest = apicontractsv1.transactionRequestType()
    transactionrequest.transactionType = "authCaptureTransaction"
    transactionrequest.amount = TOTAL
    transactionrequest.payment = payment
    transactionrequest.order = order
    transactionrequest.billTo = customerAddress
    transactionrequest.customer = customerData
    transactionrequest.transactionSettings = settings
    transactionrequest.lineItems = line_items

    # Assemble the complete transaction request
    createtransactionrequest = apicontractsv1.createTransactionRequest()
    createtransactionrequest.merchantAuthentication = merchantAuth
    createtransactionrequest.refId = "MerchantID-0001"
    createtransactionrequest.transactionRequest = transactionrequest
    # Create the controller
    createtransactioncontroller = createTransactionController(
        createtransactionrequest)
    createtransactioncontroller.execute()

    response = createtransactioncontroller.getresponse()

    if response is not None:
        # Check to see if the API request was successfully received and acted upon
        if response.messages.resultCode == "Ok":
            # Since the API request was successful, look for a transaction response
            # and parse it to display the results of authorizing the card
            if hasattr(response.transactionResponse, 'messages') is True:
                print('Successfully created transaction with Transaction ID: %s' % response.transactionResponse.transId)
                print('Transaction Response Code: %s' % response.transactionResponse.responseCode)
                print('Message Code: %s' % response.transactionResponse.messages.message[0].code)
                print('Description: %s' % response.transactionResponse.messages.message[0].description)
            else:
                print('Failed Transaction.')
                if hasattr(response.transactionResponse, 'errors') is True:
                    print('Error Code:  %s' % str(response.transactionResponse. errors.error[0].errorCode))
                    print(
                        'Error message: %s' % response.transactionResponse.errors.error[0].errorText)
        # Or, print errors if the API request wasn't successful
        else:
            print('Failed Transaction.')
            if hasattr(response, 'transactionResponse') is True and hasattr( response.transactionResponse, 'errors') is True:
                print('Error Code: %s' % str(response.transactionResponse.errors.error[0].errorCode))
                print('Error message: %s' % response.transactionResponse.errors.error[0].errorText)
            else:
                print('Error Code: %s' % response.messages.message[0]['code'].text)
                print('Error message: %s' % response.messages.message[0]['text'].text)
    else:
        print('Null Response.')

    return response
