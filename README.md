# Go1 Leads

Sync leads of various platform like Trade india, Indiamart , Facebook etc..

## Installation

1. [Install Bench](https://github.com/frappe/bench).
2. Install ERPNext
 ```
 bench get-app erpnext
 ```
3. Install Go1 Lead app
```
bench get-app https://github.com/TridotsTech/go1_lead
```
4.  Install ERPNext on your site
```
bench --site <sitename> install-app erpnext
```
5. Install Go1 Lead on your site
```
bench --site <sitename> install-app go1_leads
```

### Setup
#### Lead Sync for Tradeindia and Indiamart will happen in the frequency of 15 mins

#### Trade india Setup
1. [Login to your Trade India Account](https://mti.tradeindia.com/)
2. Setup credentials  , Click on your profile and move to Dashboard  
    Dashboard > Leads and Inquiries > My Inquiry API  
    Copy and paste the necessary details on Go1 Lead Integration


#### Indiamart Setup
1. [Login to your indiamart account](https://www.indiamart.com/)
2. Setup credentials  
    Get credentials for Pull Lead  
    Copy and paste the necessary details on Go1 Lead Integration

 You can pull leads manually using Pull Lead button with specific dates or default today leads will be pulled


#### License

mit