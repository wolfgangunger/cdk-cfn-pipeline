

# cdk-codepipeline
cdk project with codepipeline to generate pipelines for cloud formation templates
it will create a pipeline generator pipeline which will create one pipeline for each cloudformation template in the cfn-repo  
for this architecture 2 approaches are possible:  
to create this generator pipeline once in a toolchain account and create all cfn-pipelines for all accounts/stages in there.  
possible, but this would require cross account roles and setup and complicate this project, make it harder to understand.  
my multi branch pipeline follows this approach  
I implemented the 2nd more easy and clear approach.  
in each account/stage the pipeline generator must be deployed to generate the cfn-templates in the account where the stacks should be deployed.  
thus no cross account roles are complicating the project 
note, that you have to deploy the generator pipeline in dev, qa and prod for example and adapat the stage name in the cdk.json each time.  


## project strucure
  
README  
cdk.json ( adpate the variables)  
requirements.txt  
app.py ( the main python file for the cdk commands, creates the Pipeline Stack)  
infrastructure ( project specific cdk classes and constructs)  
 

## architecture
![image](https://github.com/wolfgangunger/cdk-codepipeline-multibranch/blob/main/feature-pipeline.jpg)
The project contains object orientated cdk design  
therefor cdk constructs are either in   
generic/infrastructure (reusable generic classes)  
or  
infrastructure (project specific classes)  


## setup project
### cdk commands
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
cdk synth
### codestar
create codestar connection in AWS Toolchain Account ( if you want to use code star. otherwise you have to configure your Github in the source )
connect the repo for this pipeline and also the repo for the cloud formation templates  

### cdk.json
adapt the cdk.json for your accounts, also codestar connection url
adapt repo  names etc

### deploy the roles to the stage accounts
deploy the 3 roles to dev, qa and prod
for example with : cdk-deploy bootstrap-qa-role-stack
#### bootstrap
bootstrap the toolchain & stage accounts
with toolchain credentials
cdk bootstrap   --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess  aws://12345678912/us-east-1




### deploy the pipeline via cli    
cdk deploy  cdk-pipeline-multi-branch
  
now the pipeline should be ready and will be triggered on any push to the repo  

### deploy the feature-branch-pipeline-generator via cli    
cdk deploy feature-branch-pipeline-generator
Edit the secret github_webhook_secret to keep a structure like this:
{"SecretString" : "xxxxx"}

### edit github-actions-demo.yml
edit the webhook_url to your api gateway url ( or custom domain)  
change action triggers if needed   

### create branch and push to see the new feature pipeline gets generated
create a new branch  
git checkout -b feature/branch1  
and push to your repo  
the pipeline will be generated

### create PR and merge 
the pipeline will be destroyed  

## tests
### infrastructure tests
pytest -vvvv -s generic/infrastructure/tests
pytest -vvvv -s infrastructure/tests
### lambda tests 
pytest -vvvv -s infrastructure/lambdas/tests
### integration tests
only dummy tests in this example 
### acceptance tests
only dummy tests in this example 



