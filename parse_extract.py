import re


def html_page_header(ticket_number):
    html_header1 = """
    <!DOCTYPE html>
        <html>
        <head>"""
    html_header2 = '<title>{}</title>'.format(ticket_number)
    html_header3 = """<meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <!-- Bootstrap CSS -->
    <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css' rel='stylesheet' crossorigin='anonymous'>

    <link rel='stylesheet' href='../jira.css'>
        </head>
        <body>"""

    return html_header1 + html_header2 + html_header3


def html_page_footer():
    html_footer = """
        </body>
    </html>
    """
    return html_footer


# Open file
f = open('./source/B4CASMPI_AllQOZBTickets.htm', mode="r", encoding="utf-8")

output_directory = './output'
hr_term = '<hr class=\'fullcontent\'>'
h3_term = '<h3 class="formtitle">'
table_term = '<table class="tableBorder"'

line_number = 0
document_count = 0
name_flag = 0
current_document = ''

for line in f:
    line_number = line_number + 1

    if name_flag == 1:
        # This line will hold the ticket number and title
        # print('{}'.format(line))
        # Parse out the ticket number
        pattern = '\[(.*)\]'
        match = re.search(pattern, line)
        if match:
            # print(match.group()[1:-1:])
            ticket_number = match.group()[1:-1:]

        # Parse out the title
        pattern = '>(.*)<'
        match = re.search(pattern, line)
        if match:
            # print(match.group()[1:-1:])
            ticket_title = match.group()[1:-1:]
        print('Jira: {} - Title: {}'.format(ticket_number, ticket_title))

        name_flag = 0

    if line.find(table_term) != -1:
        # Start of document..
        document_count = document_count + 1
        # Reset the current_document
        current_document = ''
        print('')
        print('..line {}; document {} => {}'.format(line_number, document_count, table_term))

    if line.find(h3_term) != -1:
        name_flag = 1
        print('..line {}; document {} => {}'.format(line_number, document_count, h3_term))

    if line.find(hr_term) != -1:
        # End of document
        # Write output to new file
        output_filename = output_directory + '/' + ticket_number + ' - ' + ticket_title + '.htm'
        with open(output_filename, 'w') as f_output:
            f_output.write(html_page_header(ticket_number))
            f_output.write(current_document)
            f_output.write(html_page_footer())

        print('..line {}; document {} => {}'.format(line_number, document_count, hr_term))

    current_document = current_document + '\n' + line

f.close()
