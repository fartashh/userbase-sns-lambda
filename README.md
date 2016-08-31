# Serverless Push Notification System in AWS  

Collection of 9 lambda functions, which handel user-based server-less push-notification system. 
Server less push notification system by using AWS Lambda and SNS. It is scalable, flexible and integrable with any user management system. It is designed to send user based push notification.


## Technology Stack
- AWS lambda
- AWS SNS
- AWS API Gateway
- AWS RDS
- Python 2.7


{{< img src="/images/post/lambda_sns/aws_sns_lambda.png" title="" class="align-center">}}
One of the best approaches to increase and keep customer engagement with your app is push notification and as you may know 
there are many services such SNS, Firebase, Pushwoosh, Urban Airship, carnival and etc., to address this need.

Recently at Mindvalley we have decided to use one of the available solutions to send push notifications to our web and mobile users.
The new service should support following requirements;

 * Integrable with our user management system
 * Authentication and Authorization with Auth0
 * Send notification to **user** (multiple devices, multiple platform) not only single device
 * Schedule notification
 * Flexible user segmentation
 * Comprehensive API to manage notification system 


## Proposed Solution 

After doing some research and comparing aforementioned solutions I came up with the idea of using server less approach.
The proposed system used AWS SNS, RDS, Lambda, and API Gateway to fulfill all requirements.
 
{{< img src="/images/post/lambda_sns/sns_architecture.png" title="" class="align-center">}}

