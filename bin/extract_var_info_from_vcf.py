import os
import argparse
from cyvcf2 import VCF


#---------------#
# Class VarData #
#---------------#
# Contains the variant information

class VarData:

    def __init__(self,id,chr,start,end,alleles):
        self.id = id
        self.chr = chr
        self.start = start
        self.end = end
        self.alleles = alleles

    def format_data_to_row(self):
        return f'{self.id}\t{self.id}\t{"/".join(self.alleles)}\t{self.chr}\t{self.start}\t{self.end}\t0'


#---------------#
# Class VarList #
#---------------#
# Read VCF file and extract variants information

class VarList:

    def __init__(self,vcf_filepath,output_filename):
        '''
        > Variables:
            - vcf_filepath: Path to the filtered VCF file
            - output_filename: Path to the output file (listing the variants and their extracted information)
        '''
        self.VCF = None
        self.vardata_list = []
        self.output_filename = output_filename
        if os.path.isfile(vcf_filepath):
            self.VCF = VCF(vcf_filepath)

    def parse_vcf(self):
        '''
        Read each line of the VCF file, parse its content and store the variant information into a list.
        '''

        for variant in self.VCF:
            id = variant.ID
            chr = variant.CHROM
            start = variant.start+1 #(cyvcf2 bug?)
            end = variant.end
            ref_al = variant.REF
            alt_al = variant.ALT
            type = variant.INFO.get('TSA')


            if type == 'insertion' or type == 'deletion':
                # Move 1 position toward 3'
                start += 1
                if start > end:
                    end = start
                # Shorten alleles
                ref_al = ref_al[1:]
                if ref_al == '':
                    ref_al = '-' 
                new_alt_al = []
                for al in alt_al:
                    new_al = al[1:]
                    if new_al == '':
                        new_al = '-' 
                    new_alt_al.append(new_al)
                alt_al = new_alt_al
            
            alleles = [ref_al]
            for al in alt_al:
                alleles.append(al)
            
            vardata = VarData(id,chr,start,end,alleles)

            self.vardata_list.append(vardata.format_data_to_row())


    def write_output(self):
        '''
        Write the collected variants information into a text-tabulated file.
        '''
        out = open(self.output_filename,'w')
        for vardata in self.vardata_list:
            out.write(f'{vardata}\n')
        out.close()


################################################################################

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--vcf", help='Path to the VCF file', required=True, metavar='INPUT_VCF')
    argparser.add_argument("--output", help='Path to the output file', required=True, metavar='OUPUT_FILE')

    args = argparser.parse_args()

    vcf_file = args.vcf
    output_file = args.output

    # Check if filtered VCF file exists
    if not os.path.isfile(vcf_file):
        print("File '"+vcf_file+"' can't be found")
        exit(1)

    # Extract the variants information from VCF and store it into a text-tabulated file
    varlist = VarList(vcf_file,output_file)
    varlist.parse_vcf()
    varlist.write_output()


if __name__ == '__main__':
    main()
