

# cloudformation-deployment-codepipeline
cdk project with codepipeline to generate pipelines for cloudformation templates deployment    
  
it will create a pipeline generator pipeline which will create one pipeline for each cloudformation template in the cfn-repo  
for this architecture 2 approaches are possible:  
to create this generator pipeline once in a toolchain account and create all cfn-pipelines for all accounts/stages in there.  
possible, but this would require cross account roles and setup and complicate this project, make it harder to understand.  
my multi branch pipeline follows this approach  
I implemented the 2nd more easy and clear approach for this pipeline.    
in each account/stage the pipeline generator must be deployed to generate the cfn-templates in the account where the stacks should be deployed.  
thus no cross account roles are complicating the project, the stage account is considered the same as the toolchain account 
note, that you have to deploy the generator pipeline in dev, qa and prod for example and adapat the stage name in the cdk.json each time.  

to be able to use this pipeline, your cloudformation repo must follow a convention on naming folders, templates and parameter json files, see below  

## project strucure
  
README  
cdk.json ( adapt the variables !)  
requirements.txt  
app.py ( the main python file for the cdk commands, creates the Pipeline Stack)  
infrastructure ( project specific cdk classes and constructs like the pipelines)  
 

## architecture
![image](https://github.com/wolfgangunger/cdk-cfn-pipeline/blob/main/pipeline-cfn.jpg)


## setup project
### cdk initial commands
python -m venv .venv  
.venv\Scripts\activate.bat  
pip install -r requirements.txt  

### codestar
create codestar connection in AWS Toolchain Account ( if you want to use code star. otherwise you have to configure your Github in the source )
connect the repo for this pipeline and also the repo for the cloud formation templates  

### cdk.json
adapt the cdk.json for your accounts, also codestar connection url
adapt repo names etc


#### bootstrap
bootstrap the toolchain & stage accounts
with toolchain credentials
cdk bootstrap   --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess  aws://12345678912/us-east-1
cdk bootstrap   --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess  aws://039735417706/eu-west-2

### cdk commands to test syntax of project and cdk.json values 
cdk ls  
will show you :  
bootstrap-role-stack ( must be deployed)  
cfn-deploy--pipeline-generator  ( must be deployed)  
cfn-deploy--pipeline-generator/pipeline-generator-bootstrap-stage/cfn-pipeline-template ( will be deployed by the generator pipeline )  

cdk synth  

### deploy pipeline role via cli
cdk deploy bootstrap-role-stack

### deploy the pipeline via cli    
cdk deploy  cfn-deploy--pipeline-generator
  

when the pipeline-generator pipelines runs it will create first a template-pipeline for cloudformation deployments ( not runnable due to params in stage)  
and then create n pipelines for each cloudformation template in the cfn-repo, which will look like this:  
![image](https://github.com/wolfgangunger/cdk-cfn-pipeline/blob/main/pipeline-cfn2.jpg)

the pipeline generator pipeline got 2 input sources:  
the cdk pipeline itself
the cloudformation repo for which the cfn-pipelines should be generated 

please see my git repo "cfn-for-pipeline" as example :
structure must be:   
cfn_[foldername]  
-template.yaml  
-params_[stage].json  

example :   
cfn_001_simple_user  
-template.yaml  
-params_dev.json  
-params_qa.json  
-params_prod.json  

to deploy the cloudformation templates, trigger the pipeline for this stack after updating  

you will see as many pipelines as you have subfolders (cfn_[foldername]) with templates in your cfn-repo  




