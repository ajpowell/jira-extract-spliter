# Using details from here: https://jira.readthedocs.io/index.html

from jira import JIRA

username = ''
password = ''
jira = JIRA('https://jira.int.support.awsplatform.co.uk/jira',
            auth=(username, password))

issue = jira.issue('B4CASMPI-8357')

summary = issue.fields.summary
print('Summary: {}'.format(summary))
print('Attachments')
for attachment in issue.fields.attachment:
    print("> Name: '{filename}', size: {size}".format(
        filename=attachment.filename, size=attachment.size))
    # to read content use `get` method:
    # print("> Content: '{}'".format(attachment.get()))
    f = open('./tmp/' + attachment.filename, 'wb')
    f.write(attachment.get())
    f.close()
