

# cloudformation-deployment-codepipeline
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
![image](https://github.com/wolfgangunger/cdk-cfn-pipeline/blob/main/pipeline-cfn.jpg)


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


#### bootstrap
bootstrap the toolchain & stage accounts
with toolchain credentials
cdk bootstrap   --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess  aws://12345678912/us-east-1




### deploy the pipeline via cli    
cdk deploy  cfn-deploy--pipeline-generator
  

when the pipeline-generator pipelines runs it will create first a template-pipeline for cloudformation deployments ( not runnable due to params in stage)  
and then create n pipelines for each cloudformation template in the cfn-repo, which will look like this:  
![image](https://github.com/wolfgangunger/cdk-cfn-pipeline/blob/main/pipeline-cfn2.jpg)

to deploy the cloudformation templates trigger the pipeline for this stack after updating  




