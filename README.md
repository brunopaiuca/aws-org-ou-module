# aws-org-ou-module
Python script to provision AWS Organization Unit

I wrote it to support one project to provisione AWS multi account environment, using AWS Organization. I used Terraform to create the organization, accounts and policys, but they does not have a module to manage OU.



# Json 

You need to create a Json File to support the Organization Hierarchy.

```
{
	"topLevelOUID": "r-abcd",
	"OUs": [
                {
			"OUName": "Core_Accounts"
		},
		{
			"OUName": "WorkLoad_Accounts"
		},
		{
			"OUName": "Developer_Accounts"
		}, 
		{
			"ParentOUName": "WorkLoad_Accounts",
			"OUName": "Production_WorkLoad"
		},
		{
			"ParentOUName": "WorkLoad_Accounts",
			"OUName": "Staging_WorkLoad"
		}
  ]
}
```

topLevelOUID	-> Roou OU ID  
OUName		-> Name of the Organization Unit  
ParentOUName	-> Name of the Parent OU to create the hierarchy, if this key does not exist in the OU will be created below the Root OU.

# Build

```
docker build . --tag aws-organization-unit-bootstrap
```

# Deploy OUs

Dont forget to pass the AWS Credentials when start the container

```
docker container run aws-organization-unit-bootstrap -e AWS_ACCESS_KEY=XXXX -e AWS_SECRET_KEY=XXXX
```

The container will run and die at the finish of the creation of the structure. Put it in you CI server to run continuosly.

# running 

``` 
 $ V=1 ; until [ "${V}" == '' ] ; do V=$(python ou_provisioner.py) ; echo $V ; sleep 1 ; done


