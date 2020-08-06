# Azure Function (Python) sample to call API, comparing previously state and send alert message over WhatsApp via Twilio.

This is demostration of using Azure Function (Python) to obtain latest number of confirmed COVID-19 cases in particular Hong Kong district from HK Gov Open Data API ([Data in Coronavirus Disease (COVID-19)](https://data.gov.hk/en-data/dataset/hk-dh-chpsebcddr-novel-infectious-agent) [Data.gov.hk](https://data.gov.hk/en/)). This is basic ([Timer Trigger](https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-timer?tabs=csharp) Azure Function to regularly call API, comparing previous state of result and send alert message over WhatsApp via ([Twilio](https://www.twilio.com/whatsapp)).

* __init__.py > main function code
* requirements > required libraries to run this code
* function.json > timer trigger function configuration

![alt text](https://github.com/easonlai/azure_function_python_sample_01/blob/master/git-images/diagram1.PNG)