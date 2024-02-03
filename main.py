from classif.prediction import predict_dbaasp
import sys

"""
curl -X 'GET' \
  'https://dbaasp.org/peptides?sequence.value=WRPGRWWRPGRW' \
  -H 'accept: application/json'

curl -X 'GET' \
  'https://dbaasp.org/peptides?sequence.value=NLVSGLIEARKYLEQLHRKLKNCKV' \
  -H 'accept: application/json' 
"""

if __name__ == "__main__":
    path = sys.argv[1]

    predict_dbaasp(path)
