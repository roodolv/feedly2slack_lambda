## FeedlyのDynamoDB用JSON payload
```
{TableName}:feedly
{ItemNumber}:9
{items(Feedly)}:[
        {Key0}:'id'
        {Key1}:'title'
        {Key2}:['alternate'][0]['href']
        {Key3}:['origin']['title']
        {Key4}:['origin']['htmlUrl']
        {Key5}:['enclosure'][0]['href']
        {Key6}:'author'
        {Key7}:['summary']['content']
        {Key8}:['content']['content']
]
{item(dynamo)}:[
        {Partition Key(Key0)}:'id'
        {Key1}:'art_title'
        {Key2}:'art_url'
        {Key3}:'author_name'
        {Key4}:'author_url'
        {Key5}:'art_image_url'
        {Key6}:'written_by'
        {Key7}:'summary'
        {Key8}:'content'
]
```

注: FeedlyのフィードはKey6～8を含んでいない場合があるためLambdaスクリプト側で`if-else`分岐処理

## Lambda実行ロール用ポリシー
- `GetRecords`
- `GetShardIterator`
- `DescribeStream`
- `ListStreams`

上記4つをIAMからIAMロールに追加するためには
`AWSLambdaDynamoDBExecutionRole`
を追加する

## Lambda(feedly2db) environ(#blog)
```
{Python version}:3.7.2(Original:3.6.1)
{Module requirement}:requests, boto3
{FEEDLY_URL}:別記
{FEEDLY_TOKEN}:別記
{ERROR_SLACK_URL}:別記
{ERROR_SLACK_CHANNEL}:aws-error
{DYNAMO_TABLE}:feedly (feedly-blog)
{INTERVAL_MINUTE}:600
{FEED_COUNT}:30
{LOG_LEVEL}:INFO(もしくはDEBUG)
```

## Lambda(db2slack) environ(#blog)
```
{Python version}:3.7.2(Original:3.6.1)
{Module requirement}:requests, boto3
{SLACK_URL}:別記
{SLACK_CHANNEL}:feed-blog
{ERROR_SLACK_URL}:別記
{ERROR_SLACK_CHANNEL}:aws-error
{LOG_LEVEL}:INFO(もしくはDEBUG)
```

## Slack-Apps(Feedly to Slack)
- Channel Name1: feed-blog
    - Incoming Webhook URL1: deleted
- Channel Name2: feed-dev
    - Incoming Webhook URL2: deleted
- Channel Name3: aws-error
    - Incoming Webhook URL3: deleted

## Slack-Apps(AWS Notifier)
- Channel Name1: aws-signin
    - Incoming Webhook URL1: deleted

## Feedly API
- user id: deleted(2019/09/05)
- API URL(#blog): `https://cloud.feedly.com/v3/streams/contents?streamId=user/<SECRET>/category/<CATEGORY_NAME>`
- Developer Access Token: deleted(2019/09/05)

## フィード用画像(GoogleDrive)
- 共有用URL: deleted
