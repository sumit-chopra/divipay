# DiviPay Backend Challenge

This backend challenged has been solved using the following tools:
- Python
- Django
- Django Rest Framework
- SQLite

## Controls

Controls are defined as key-value pair  of control_name and control_value

There are 4 controls defined in the configuration:
- MER_NAME
- MER_CAT
- MIN_AMT
- MAX_AMT

But the implementation takes care of defining “N” number of controls without requiring any code changes.

Controls are saved per card in the database as follows:

| CONTROL_ID | CARD_ID | CONTROL_NAME | CONTROL_VALUE |
| --- | --- | --- | --- |
| 1 | 9d9e91d6-312c-4641-b5de-9a0bfa7deb52 | MER_NAME | Wwoolworths |
| 2 | 9d9e91d6-312c-4641-b5de-9a0bfa7deb52 | MER_NAME | Coles       |
| 3 | 9d9e91d6-312c-4641-b5de-9a0bfa7deb52 | MER_NAME | AWS         |
| 4 | 9d9e91d6-312c-4641-b5de-9a0bfa7deb52 | MAX_AMT  | 1000        |

Ideally, an external rule based engine should be used to validate and match transaction against the Controls.
In interest of time, a small rule based engine has been developed as part of this implementation. 

## Rules Engine
Before creating a control, it needs to be defined in settings.py — CONTROL_DEFINITION

As of now, Control could either be a String type or Integer type. 
Control definition for a String type control looks as below :
```
{
	"MER_NAME" : {
		"type" : "String",
		"input_validation" : {
			"can_multiple_exists" : True,
			"choices" : ["Woolworths", "Coles"]
		},
		"src_comparison" : {
			"variable_name" : "merchant",
			"operator" : "IN"
		}
}
```
Control definition for a Integer type control looks as below :

```
{
	“MAX_AMT" : {
		"type" : "Integer",
		"input_validation" : {
			"can_multiple_exists" : False,
			"min_value" : 0,
			"max_value" : 1000,
		},
		"src_comparison" : {
			"variable_name" : "amount",
			"operator" : "LTE"
		}
}
```
**input_validation** - Defines the validations that needs to be done on the control_value while a control is getting added via the Create Control API. 

For Integers, the incoming value can be checked for a minimum allowable value and maximum allowable value for a control saved in DB.

For Strings, the incoming value can be checked against a list of allowed values.

**can_multiple_exists** - Defines whether a specific type of control can have multiple entries in the database for a single card. MER_NAME and MER_CAT can have multiple entries for a card, while MIN_AMT and MAX_AMT can not have multiple entries for a card.

**src_comparison** - Defines the value stored for a control in Database needs to be compared against which variable of transaction object. 

In this example, MER_NAME control saved in DB will be matched up against the value of “merchant” key in the transaction object.

MAX_AMT control saved in DB will be matched up against the value of “amount” in the transaction object.

**operator** - Defines which operation will be used to make this comparison. e.g. IN, EQ (Equals), LT (Less Than), GT (Greater Than), LTE (Less Than Equal To), GTE (Greater Than 
Equal To)
Control definitions can be added or removed and new controls can be defined in the configuration without requiring any code changes.

Every card needs to have at least mandatory controls configured for them so that a transaction can be processed. These are defined by the property in settings.py. 

Example configuration looks like as follows :
```
MANDATORY_CONTROLS = [
    "MAX_AMT", ["MER_NAME", "MER_CAT"]
    ]
```
This means every control should have MAX_AMT control defined for them and either of MER_NAME or MER_CAT defined for them.

The property can be modified to specify the mandatory_controls as per the requirements.


## APIs

### View Controls

| HTTP_REQUEST | |
| --- | --- |
| URL | http://127.0.0.1:8000/cardcontrol/api/v1/card/<card_id>/control |
| METHOD | GET |
| HEADER | Authorization: Token 87a333253610bbaf15324c194d5582b399930ea5 |
| CURL | curl http://127.0.0.1:8000/cardcontrol/api/v1/card/9d9e91d6-312c-4641-b5de-9a0bfa7deb52/control -H "Authorization: Token 87a333253610bbaf15324c194d5582b399930ea5” |

**Tasks:**

- Make sure that an authenticated user is invoking this API
- Retrieve the controls for the given card id from DB and return

### Create Control

| HTTP_REQUEST | |
| --- | --- |
| URL | http://127.0.0.1:8000/cardcontrol/api/v1/card/<card_id>/control |
| METHOD | POST |
| HEADER | Authorization: Token 87a333253610bbaf15324c194d5582b399930ea5 |
| BODY | {"control_name":"MER_NAME", “control_value":"Woolworths"} |
| CURL | curl http://127.0.0.1:8000/cardcontrol/api/v1/card/9d9e91d6-312c-4641-b5de-9a0bfa7deb52/control -H "Authorization: Token 87a333253610bbaf15324c194d5582b399930ea5" -X POST -d ‘{"control_name":"MER_NAME", “control_value":"Woolworths"}' -H “Content-Type:application/json” |


**Tasks:**

- Make sure that an authenticated user is invoking this API
- Make sure that user who has created the card is creating the control
- Make sure control_name is a valid control name
- Run input validations on control_value to make sure it is legitimate
- Save it in DB


### Delete Control

| HTTP_REQUEST | |
| --- | --- |
| URL | http://127.0.0.1:8000/cardcontrol/api/v1/card/<card_id>/control/<control_id> |
| METHOD | DELETE |
| HEADER | Authorization: Token 87a333253610bbaf15324c194d5582b399930ea5 |
| CURL | curl -X DELETE http://127.0.0.1:8000/cardcontrol/api/v1/card/9d9e91d6-312c-4641-b5de-9a0bfa7deb52/control/17 -H "Authorization: Token 87a333253610bbaf15324c194d5582b399930ea5 |

**Tasks:**

- Make sure that an authenticated user is invoking this API
- Make sure that user who has created the card is deleting the control
- Delete the control from DB


## Helper APIs

### Create Card
 
| HTTP_REQUEST | |
| --- | --- |
| URL | http://127.0.0.1:8000/cardcontrol/stub/card |
| METHOD | POST |
| HEADER | Authorization: Token 87a333253610bbaf15324c194d5582b399930ea5 |
| CURL | curl -X POST http://127.0.0.1:8000/cardcontrol/stub/card -H "Authorization: Token 87a333253610bbaf15324c194d5582b399930ea5” |

**Tasks :**

- Hits Divi Pay Card API
- Saves the card object in the Database

### Process Transaction

| HTTP_REQUEST | |
| --- | --- |
| URL | http://127.0.0.1:8000/cardcontrol/stub/txn |
| METHOD | GET |
| CURL | curl -X POST http://127.0.0.1:8000/cardcontrol/stub/txn  |


**Tasks :**

- Hits Divi Pay API to fetch the transaction
- Retrieve the controls from DB for the corresponding card id
- SQL Query = Select control_name, group_concat(control_value) from control where card_id = ? group by control_name
- Makes sure that this card has at least the mandatory controls configured on it
- Process all the controls
- Ideally I would have loved to use an external rules engine to implement this and would have kept it outside of the control. In interest of time, I have implemented a small rules engine which is fairly independent of the application logic to process these controls. 


## Authentication

Apart from Transaction API, other APIs require a valid token to be used. For authentication, Django Rest framework’s auth module is being used.
Token generation for a user is out of scope of this implementation.
To create a valid token, following needs to be done:

- python manage.py createsuperuser
- python manage.py drf_create_token <user_name_of_user_created_step_1>



## Steps to be followed

- Run the application. Ensure the environment is set up properly.
- Make DB migrations
- Create a user and token as specified in [AUTHENTICATION](#authentication) section
- Create a card as specified in [Create Card API](#create-card) section
- Create controls as specified in [Create Control API](#create-control) section
- Create controls as defined in MANDATORY_CONTROL settings
- Retrieve the controls defined as specified in [View Controls API](#view-controls) section
- Process a transaction by invoking [Dummy Transaction API](#process-transaction)

Please note : DiviPay API Key has been removed from settings_local.py. Please add the value there to run the application.
