from classif.ampscannerv2.api import predict_ampscanner
from argparse import ArgumentParser

if __name__ == "__main__":
    # predict_stm('resources/TEST.fasta', 'outputs')
    parser = ArgumentParser()
    parser.add_argument('-i', '--input_path', type=str, required=True)
    parser.add_argument('-o', '--output_path', type=str, required=True)
    args = parser.parse_args()
    predict_ampscanner(args.input_path, args.output_path)
