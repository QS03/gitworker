##### Install git
    `sudo apt install git`
    
    
##### Create source/target repositories on github account
Bot will clone both repositories, random copy files from source repository to target repository.
Random commit will be taken following the configuration.


##### Create `config.json` in the script directory and fill out the configuration.
```json
{
  "email": "{your github email}",
  "access_token": "{ your github access token }",
  "source_repo": "{ source repository url }",
  "target_repo": "{ target repository url }",
  "start_date": "2015-01-01",
  "end_date": "2017-01-01",
  "exclude_days": [] ,
  "max_commit": 10,
  "everyday": false
}
``` 

Run the bot with root privilege.

### Have fun!