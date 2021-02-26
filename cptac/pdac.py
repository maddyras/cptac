#   Copyright 2018 Samuel Payne sam_payne@byu.edu
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import pandas as pd
import numpy as np
import os
import warnings
import datetime

from .dataset import Dataset
from .dataframe_tools import *
from .exceptions import FailedReindexWarning, PublicationEmbargoWarning, ReindexMapError


################################################################################
# HOW TO USE THIS TEMPLATE FILE
#
# To make a class for a new dataset, copy this file and fill in the indicated
# sections, as described below.
#
# This file has sections marked with the word FILL, usually in triple quotes or
# preceded by three hashtags (###). To adapt this file for a new dataset,
# replace all of those marked fields with the proper values for your dataset.
# Additionally, there are some example code sections marked with START EXAMPLE 
# CODE and END EXAMPLE CODE. You need to replace the example code with the
# proper code for processing your dataset.
#
# This file uses dataframe processing functions imported from
# cptac/dataframe_tools.py. For more information on how to use those functions,
# you can read their docstrings in that file.
#
# If there's something confusing about this file, look at the files for existing
# datasets to provide examples of how this file would actually be implemented.
# If the new dataset you're adding has something weird that isn't addressed in
# this file, check the other datasets to see if any of them deal with a similar
# issue.
################################################################################

###FILL: Put in the actual name/acronym for the cancer type as the class name in the line below, in UpperCamelCase.
### For example, the endometrial dataset's class is called Endometrial; the BRCA dataset's class is called Brca; and the ccRCC dataset's class is called Ccrcc.
class Pdac(Dataset):

    def __init__(self, version="latest", no_internet=False):
        """Load all of the dataframes as values in the self._data dict variable, with names as keys, and format them properly.

        Parameters:
        version (str, optional): The version number to load, or the string "latest" to just load the latest building. Default is "latest".
        no_internet (bool, optional): Whether to skip the index update step because it requires an internet connection. This will be skipped automatically if there is no internet at all, but you may want to manually skip it if you have a spotty internet connection. Default is False.
        """

        # Set some needed variables, and pass them to the parent Dataset class __init__ function

        # This keeps a record of all versions that the code is equipped to handle. That way, if there's a new data release but they didn't update their package, it won't try to parse the new data version it isn't equipped to handle.
        valid_versions = ["1.0"]

        ###FILL: Insert actual data files below
        data_files = {
            "1.0": [
            "clinical_table_140.tsv.gz",
            "microRNA_TPM_log2_Normal.cct.gz",
            "microRNA_TPM_log2_Tumor.cct.gz",
            "meta_table_140.tsv.gz",
            "mRNA_RSEM_UQ_log2_Normal.cct.gz",
            "mRNA_RSEM_UQ_log2_Tumor.cct.gz",
            "PDAC_mutation.maf.gz",
            "phosphoproteomics_site_level_MD_abundance_normal.cct.gz",
            "phosphoproteomics_site_level_MD_abundance_tumor.cct.gz",
            "proteomics_gene_level_MD_abundance_normal.cct.gz",
            "proteomics_gene_level_MD_abundance_tumor.cct.gz",
            "RNA_fusion_unfiltered_normal.tsv.gz",
            "RNA_fusion_unfiltered_tumor.tsv.gz",
            "SCNA_log2_gene_level.cct.gz"],
        }

        # Call the parent class __init__ function
        super().__init__(cancer_type="pdac", version=version, valid_versions=valid_versions, data_files=data_files, no_internet=no_internet)

        # Load the data into dataframes in the self._data dict
        loading_msg = f"Loading {self.get_cancer_type()} v{self.version()}"
        for file_path in self._data_files_paths: # Loops through files variable

            # Print a loading message. We add a dot every time, so the user knows it's not frozen.
            loading_msg = loading_msg + "."
            print(loading_msg, end='\r')

            path_elements = file_path.split(os.sep) # Get a list of the levels of the path
            file_name = path_elements[-1] # The last element will be the name of the file. We'll use this to identify files for parsing in the if/elif statements below
            mark_normal = lambda s: s + ".N"
            remove_type_tag = lambda s: s[:-2]

            ###FILL: Insert if/elif statements to parse all data files. Example:
            ###START EXAMPLE CODE###############################################
            if file_name == "clinical_table_140.tsv.gz": # Note that we use the "file_name" variable to identify files. That way we don't have to use the whole path.
                df = pd.read_csv(file_path, sep='\t', index_col=0)
                df = df.rename_axis("Patient_ID", axis="index")
                df = df.sort_index()
                df.columns.name = "Name"
                self._data["clinical"] = df

            elif file_name == "meta_table_140.tsv.gz":
                df = pd.read_csv(file_path, sep='\t', index_col=0)
                df = df.sort_index()
                df.index.name = "Patient_ID"
                df.columns.name = "Name"
                self._data["derived_molecular"] = df

            elif file_name == "microRNA_TPM_log2_Normal.cct.gz":
                df_normal = pd.read_csv(file_path, sep='\t', index_col=0)
                df_normal = df_normal.sort_index()
                df_normal = df_normal.transpose()
                df_normal["Sample_Tumor_Normal"] = "Normal"
                df_normal = df_normal.rename(index=mark_normal)

                # merge tumor and normal if tumor data has already been read
                if "miRNA" in self._data:
                    df_tumor = self._data["miRNA"]
                    df_combined = pd.concat([df_normal, df_tumor])
                    df_combined.index.name = "Patient_ID"
                    df_combined.columns.name = "Name"
                    self._data["miRNA"] = df_combined
                else:
                    self._data["miRNA"] = df_normal

            elif file_name == "microRNA_TPM_log2_Tumor.cct.gz":
                df_tumor = pd.read_csv(file_path, sep='\t', index_col=0)
                df_tumor = df_tumor.sort_index()
                df_tumor = df_tumor.transpose()
                df_tumor["Sample_Tumor_Normal"] = "Tumor"

                # merge tumor and normal if normal data has already been read
                if "miRNA" in self._data:
                    df_normal = self._data["miRNA"]
                    df_combined = pd.concat([df_normal, df_tumor])
                    df_combined.index.name = "Patient_ID"
                    df_combined.columns.name = "Name"
                    self._data["miRNA"] = df_combined
                else:
                    self._data["miRNA"] = df_tumor

            elif file_name == "mRNA_RSEM_UQ_log2_Normal.cct.gz":
                # create df for normal data
                df_normal = pd.read_csv(file_path, sep='\t', index_col=0)
                df_normal = df_normal.sort_index()
                df_normal = df_normal.transpose()
                df_normal["Sample_Tumor_Normal"] = "Normal"
                df_normal = df_normal.rename(index=mark_normal)
                
                # merge tumor and normal if tumor data has already been read
                if "transcriptomics" in self._data:
                    df_tumor = self._data["transcriptomics"]
                    df_combined = pd.concat([df_normal, df_tumor])
                    df_combined.index.name = "Patient_ID"
                    df_combined.columns.name = "Name"
                    self._data["transcriptomics"] = df_combined
                else:
                    self._data["transcriptomics"] = df_normal

            elif file_name == "mRNA_RSEM_UQ_log2_Tumor.cct.gz":
                # create df for tumor data
                df_tumor = pd.read_csv(file_path, sep='\t', index_col=0)
                df_tumor = df_tumor.sort_index()
                df_tumor = df_tumor.transpose()
                df_tumor["Sample_Tumor_Normal"] = "Tumor"

                # merge tumor and normal if normal data has already been read
                if "transcriptomics" in self._data:
                    df_normal = self._data["transcriptomics"]
                    df_combined = pd.concat([df_normal, df_tumor])
                    df_combined.index.name = "Patient_ID"
                    df_combined.columns.name = "Name"
                    self._data["transcriptomics"] = df_combined
                else:
                    self._data["transcriptomics"] = df_tumor

            elif file_name == "PDAC_mutation.maf.gz":
                df = pd.read_csv(file_path, sep='\t')
                df = df[["Hugo_Symbol", "Variant_Classification", "HGVSp_Short", "Tumor_Sample_Barcode"]]
                df = df.rename({"Tumor_Sample_Barcode":"Patient_ID","Hugo_Symbol":"Gene","Variant_Classification":"Mutation","HGVSp_Short":"Location"}, axis='columns')
                df = df.sort_values(by=["Patient_ID", "Gene"])
                df = df.set_index("Patient_ID")
                df = df.rename(index=remove_type_tag)
                df.columns.name = "Name"
                self._data["somatic_mutation"] = df

            elif file_name == "phosphoproteomics_site_level_MD_abundance_normal.cct.gz":
                # create df form normal data
                df_normal = pd.read_csv(file_path, sep='\t')
                column_split = df_normal["Index"].str.rsplit("_", n=1, expand=True)
                df_normal = df_normal.assign(
                    Site = column_split[1],
                    Database_ID = column_split[0]
                )
                df_normal = df_normal.drop(columns="Index")
                df_normal = df_normal.rename(columns={"Gene":"Name"})
                df_normal = df_normal.set_index(["Name", "Site", "Peptide", "Database_ID"])
                df_normal = df_normal.sort_index()
                df_normal = df_normal.transpose()
                df_normal["Sample_Tumor_Normal"] = "Normal"
                df_normal = df_normal.rename(index=mark_normal)

                # merge tumor and normal if tumor data has already been read
                if "phosphoproteomics" in self._data:
                    df_tumor = self._data["phosphoproteomics"]
                    df_combined = pd.concat([df_normal, df_tumor])
                    df_combined.index.name = "Patient_ID"
                    #df_combined.columns.name = "Name"
                    self._data["phosphoproteomics"] = df_combined
                else:
                    self._data["phosphoproteomics"] = df_normal

            elif file_name == "phosphoproteomics_site_level_MD_abundance_tumor.cct.gz":
                df_tumor = pd.read_csv(file_path, sep='\t')
                column_split = df_tumor["Index"].str.rsplit("_", n=1, expand=True)
                df_tumor = df_tumor.assign(
                    Site = column_split[1],
                    Database_ID = column_split[0]
                )
                df_tumor = df_tumor.drop(columns="Index")
                df_tumor = df_tumor.rename(columns={"Gene":"Name"})
                df_tumor = df_tumor.set_index(["Name", "Site", "Peptide", "Database_ID"])
                df_tumor = df_tumor.sort_index()
                df_tumor = df_tumor.transpose()
                df_tumor["Sample_Tumor_Normal"] = "Tumor"
                
                # merge tumor and normal if normal data has already been read
                if "phosphoproteomics" in self._data:
                    df_normal = self._data["phosphoproteomics"]
                    df_combined = pd.concat([df_normal, df_tumor])
                    df_combined.index.name = "Patient_ID"
                    #df_combined.columns.name = "Name"
                    self._data["phosphoproteomics"] = df_combined
                else:
                    self._data["phosphoproteomics"] = df_tumor
        
            elif file_name == "proteomics_gene_level_MD_abundance_normal.cct.gz":
                df_normal = pd.read_csv(file_path, sep='\t', index_col=0)
                df_normal = df_normal.sort_index()
                df_normal = df_normal.transpose()
                df_normal["Sample_Tumor_Normal"] = "Normal"
                df_normal = df_normal.rename(index=mark_normal)

                # merge tumor and normal if tumor data has already been read
                if "proteomics" in self._data:
                    df_tumor = self._data["proteomics"]
                    df_combined = pd.concat([df_normal, df_tumor])
                    df_combined.index.name = "Patient_ID"
                    df_combined.columns.name = "Name"
                    self._data["proteomics"] = df_combined
                else:
                    self._data["proteomics"] = df_normal

            elif file_name == "proteomics_gene_level_MD_abundance_tumor.cct.gz":
                print('Found proteomics tumor')
                df_tumor = pd.read_csv(file_path, sep='\t', index_col=0)
                df_tumor = df_tumor.sort_index()
                df_tumor = df_tumor.transpose()
                df_tumor["Sample_Tumor_Normal"] = "Tumor"

                # merge tumor and normal if normal data has already been read
                if "proteomics" in self._data:
                    df_normal = self._data["proteomics"]
                    df_combined = pd.concat([df_normal, df_tumor])
                    df_combined.index.name = "Patient_ID"
                    df_combined.columns.name = "Name"
                    self._data["proteomics"] = df_combined
                else:
                    self._data["proteomics"] = df_tumor

            elif file_name == "RNA_fusion_unfiltered_normal.tsv.gz":
                df_normal = pd.read_csv(file_path, sep='\t', index_col=0)
                df_normal = df_normal.rename(columns={"Sample": "Patient_ID"})
                df_normal = df_normal.set_index("Patient_ID")
                df_normal = df_normal.rename(index=mark_normal)
                df_normal["Sample_Tumor_Normal"] = "Normal"

                if "gene_fusion" in self._data:
                    df_tumor = self._data ["gene_fusion"]
                    df_combined = pd.concat([df_normal, df_tumor])
                    df_combined.index.name = "Patient_ID"
                    df_combined.columns.name = "Name"
                    self._data["gene_fusion"] = df_combined
                else:
                    self._data["gene_fusion"] = df_normal

            elif file_name == "RNA_fusion_unfiltered_tumor.tsv.gz":
                df_tumor = pd.read_csv(file_path, sep='\t', index_col=0)
                df_tumor = df_tumor.rename(columns={"Sample": "Patient_ID"})
                df_tumor = df_tumor.set_index("Patient_ID")
                df_tumor["Sample_Tumor_Normal"] = "Tumor"

                if "gene_fusion" in self._data:
                    df_normal = self._data ["gene_fusion"]
                    df_combined = pd.concat([df_normal, df_tumor])
                    df_combined.index.name = "Patient_ID"
                    df_combined.columns.name = "Name"
                    self._data["gene_fusion"] = df_combined
                else:
                    self._data["gene_fusion"] = df_tumor

            elif file_name == "SCNA_log2_gene_level.cct.gz":
                pass
                #self._data["CNV"] = df

            ###END EXAMPLE CODE#################################################

        print(' ' * len(loading_msg), end='\r') # Erase the loading message
        formatting_msg = "Formatting dataframes..."
        print(formatting_msg, end='\r')

        # Get a union of all dataframes' indices, with duplicates removed
        ###FILL: If there are any tables whose index values you don't want
        ### included in the master index, pass them to the optional 'exclude'
        ### parameter of the unionize_indices function. This was useful, for
        ### example, when some datasets' followup data files included samples
        ### from cohorts that weren't in any data tables besides the followup
        ### table, so we excluded the followup table from the master index since
        ### there wasn't any point in creating empty representative rows for
        ### those samples just because they existed in the followup table.
        #master_index = unionize_indices(self._data) 

        # Use the master index to reindex the clinical dataframe, so the clinical dataframe has a record of every sample in the dataset. Rows that didn't exist before (such as the rows for normal samples) are filled with NaN.
        #new_clinical = self._data["clinical"]
        #new_clinical = new_clinical.reindex(master_index)

        # Add a column called Sample_Tumor_Normal to the clinical dataframe indicating whether each sample was a tumor or normal sample. Use a function from dataframe_tools to generate it.

        ###FILL: Your dataset should have some way that it marks the Patient IDs
        ### of normal samples. The example code below is for a dataset that
        ### marks them by putting an 'N' at the beginning of each one. You will
        ### need to write a lambda function that takes a given Patient_ID string
        ### and returns a bool indicating whether it corresponds to a normal
        ### sample. Pass that lambda function to the 'normal_test' parameter of
        ### the  generate_sample_status_col function when you call it. See 
        ### cptac/dataframe_tools.py for further function documentation.
        ###START EXAMPLE CODE###################################################
        #sample_status_col = generate_sample_status_col(new_clinical, normal_test=lambda sample: sample[0] == 'N')
        ###END EXAMPLE CODE#####################################################

        #new_clinical.insert(0, "Sample_Tumor_Normal", sample_status_col)

        # Replace the clinical dataframe in the data dictionary with our new and improved version!
        # self._data['clinical'] = new_clinical

        # Edit the format of the Patient_IDs to have normal samples marked the same way as in other datasets. 
        
        ###FILL: You will need to pass the proper parameters to correctly
        ### reformat the patient IDs in your dataset. The standard format is to
        ### have the string '.N' appended to the end of the normal patient IDs,
        ### e.g. the  normal patient ID corresponding to C3L-00378 would be
        ### C3L-00378.N (this way we can easily match two samples from the same
        ### patient). The example code below is for a dataset where all the
        ### normal samples have  an "N" prepended to the patient IDs. The
        ### reformat_normal_patient_ids function erases that and puts a ".N" at
        ### the end. See cptac/dataframe_tools.py for further function
        ### documentation.
        ###START EXAMPLE CODE###################################################
        #self._data = reformat_normal_patient_ids(self._data, existing_identifier="N", existing_identifier_location="start")
        ###END EXAMPLE CODE#####################################################

        # Call function from dataframe_tools.py to sort all tables first by sample status, and then by the index
        # self._data = sort_all_rows(self._data)

        # Call function from dataframe_tools.py to standardize the names of the index and column axes
        #self._data = standardize_axes_names(self._data)

        #print(" " * len(formatting_msg), end='\r') # Erase the formatting message

        
        ###FILL: If the dataset is not password access only, remove the message
        ### below. If it's under publication embargo, still remove this
        ### warning, and keep the above warning about publication embargo.
        # Print password access only warning
        warnings.warn("The pdac data is currently strictly reserved for CPTAC investigators. Otherwise, you are not authorized to access these data. Additionally, even after these data become publicly available, they will be subject to a publication embargo (see https://proteomics.cancer.gov/data-portal/about/data-use-agreement or enter cptac.embargo() to open the webpage for more details).", PublicationEmbargoWarning, stacklevel=2)