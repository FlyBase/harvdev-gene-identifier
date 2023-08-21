import os
import psycopg2
import argparse

parser = argparse.ArgumentParser()
d_txt = 'debug prints out messages.'
c_txt = 'Specify the location of the output file.'
parser.add_argument('-d', '--debug', help=d_txt,
                    default=False, action='store_true')
parser.add_argument('-f', '--filepath', help=c_txt, required=True)
args = parser.parse_args()

def create_postgres_session():
    """Connect to database."""
    user = os.environ['USER']
    password = os.environ['PGPASSWORD']
    server = os.environ['SERVER']
    try:
        port = os.environ['PORT']
    except KeyError:
        port = '5432'

    database = os.environ['DB']

    # 1. Set up database connection and queries.

    # Database connection.
    conn_string = "host=%s dbname=%s user=%s password='%s' port=%s" % (server, database, user, password, port)
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return cursor


def decode(name):
    curr_symbol = name.replace('<up>', '[')
    curr_symbol = curr_symbol.replace(r'<\up>', ']')
    curr_symbol = curr_symbol.replace('<down>', '[[')
    curr_symbol = curr_symbol.replace(r'<\down>', ']]')
    return curr_symbol

def trim_qoute_chars(name):
    return name.replace('^"|"', '')


def get_synonyms(cursor, outputfile):
    sql = """SELECT f.feature_id, f.uniquename, f.name, o.abbreviation 
               FROM feature f, organism o
               WHERE f.organism_id = o.organism_id and 
                     f.type_id = 219 and
                     f.is_obsolete = 'f' and
                     f.is_analysis = 'f' and
                     f.uniquename like 'FBgn%'
               ORDER BY f.uniquename"""

    cursor.execute(sql)
    genes = cursor.fetchall()
    SYN_NAME = 0
    SYN_SGML = 1
    SYN_TYPE = 2
    SYN_CURR = 3
    syn_sql = """ 
    SELECT DISTINCT s.name as sname, s.synonym_sgml as synonym_sgml, st.name as stype, fs.is_current
      FROM feature_synonym fs, synonym s, cvterm st
      WHERE fs.feature_id = %s and
            fs.synonym_id = s.synonym_id and
            s.type_id = st.cvterm_id and
            st.name in ('symbol', 'fullname')"""

    ### FlyBase Symbol-Synonym Correspondence Table
    ## Generated: Mon Jul 24 23:20:15 2023
    ## Using datasource: dbi:Pg:dbname=fb_2023_04_reporting;host=flysql25;port=5432...

    ##primary_FBid  organism_abbreviation   current_symbol  current_fullname        fullname_synonym(s)     symbol_synonym(s)
    # FBgn0000001     Dmel    snRNA:4.5S      small nuclear RNA 4.5S  4.5SRNA 4.5S|4.5SRNA
    # FBgn0000002     Dmel    5SrRNA  5S ribosomal RNA                2S rRNA|5S|5S RNA|5S rDNA|5S rRNA|5S-rDNA|5SRNA|5S_DM|5SrDNA|5s rRNA|Dm5S|PZ03068|RNA X|l(2)03068|rRNA
    # FBgn0000003     Dmel    7SLRNA:CR32864  Signal recognition particle 7SL RNA CR32864     RNA 7SL 7 S L RNA|7SL RNA|7SLRNA|CR32864|SRP RNA
    # FBgn0000008     Dmel    a       arc     broad angular   Arc|CG13505|CG6741|arc|bran
    # FBgn0000009     Dmel    Abnormal-abdomen        Abnormal abdomen                A|Abnormal
    # FBgn0000010     Dmel    aa      anarista        aristaless-b    al-b
    # FBgn0000012     Dmel    abb     abbreviated
    # FBgn0000013     Dmel    abd     abdominal               a(3)26|a-3
    i = 0
    with open(outputfile, 'w') as outfile:
        outfile.write('### FlyBase Symbol-Synonym Correspondence Table\n')
        outfile.write('## Generated: Mon Jul 24 23:20:15 2023\n')
        outfile.write('## Using datasource: dbi:Pg:dbname=fb_2023_04_reporting;host=flysql25;port=5432...\n')
        outfile.write('\n##primary_FBid  organism_abbreviation   current_symbol  current_fullname        fullname_synonym(s)     symbol_synonym(s)\n')

        for gene in genes:
            if args.debug:
                print(gene[0])
            i += 1
            cursor.execute(syn_sql, (gene[0],))
            syns = cursor.fetchall()
            curr_symbol = ''
            curr_fname = ''
            fullnames = []
            syn_list = []
            for syn in syns:
                # DISTINCT s.name as sname, s.synonym_sgml as synonym_sgml, st.name as stype, fs.is_current
                # name 0, sgml 1, cv name 2, is current 3
                if syn[SYN_NAME] == 'unnamed':
                    continue
                if syn[SYN_CURR] and syn[SYN_TYPE] == 'symbol':
                    curr_symbol = decode(syn[SYN_NAME])
                elif syn[SYN_CURR] and syn[SYN_TYPE] == 'fullname':
                    curr_fname = decode(syn[SYN_NAME])
                elif not syn[SYN_CURR] and syn[SYN_TYPE] == 'fullname':
                    syn_str = trim_qoute_chars(syn[SYN_NAME])
                    fullnames.append(syn_str)
                    if syn[SYN_SGML] != syn[SYN_NAME]:
                        sgml = decode(syn[SYN_SGML])
                        sgml = trim_qoute_chars(sgml)
                        fullnames.append(sgml)
                elif not syn[SYN_CURR] and syn[SYN_TYPE] == 'symbol':
                    syn_str = trim_qoute_chars(syn[SYN_NAME])
                    syn_list.append(syn_str)
                    if syn[SYN_SGML] != syn[SYN_NAME]:
                        sgml = decode(syn[SYN_SGML])
                        sgml = trim_qoute_chars(sgml)
                        syn_list.append(sgml)
                else:
                    print("\t\tno synonyms linked to this gene...\n")
                if args.debug:
                    print(f"gene {gene[1]}: {syn}")
            outfile.write(f"{gene[1]}\t{gene[3]}\t{curr_symbol}\t{curr_fname}\t{'|'.join(fullnames)}\t{'|'.join(syn_list)}\n")


def start_process():
    cursor = create_postgres_session()
    get_synonyms(cursor, f"{args.filepath}/fb_synonym_latest.tsv")

start_process()