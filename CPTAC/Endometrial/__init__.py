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

import os
import sys
import webbrowser
import textwrap
import pandas as pd
from .dataframe import DataFrameLoader
from .utilities import Utilities

def warning():
    print("\n","******PLEASE READ******")
    warning = "WARNING: This data is under a publication embargo until July 1, 2019. CPTAC is a community resource project and data are made available rapidly after generation for community research use. The embargo allows exploring and utilizing the data, but the data may not be in a publication until July 1, 2019. Please see https://proteomics.cancer.gov/data-portal/about/data-use-agreement or enter embargo() to open the webpage for more details."
    wrapped_list = textwrap.wrap(warning)
    for line in wrapped_list:
        print(line)

"""
Creates dictionary for linking Patient_Id with individual sample number (i.e. C3L-00006 with S001)
"""
def create_patient_ids(clinical): #private
    c = clinical[["Patient_ID"]][0:103] # S105 maps back to S001
    s = c.index
    dictPrepDf = c.set_index('Patient_ID')
    dictPrepDf['idx'] = s
    patient_ids = dictPrepDf.to_dict()['idx']
    return patient_ids
def link_patient_ids(patient_ids, somatic): #private
    s = []
    for x in somatic["Patient_Id"]:
        if x in patient_ids.keys():
            s.append(patient_ids[x])
        else:
            s.append("NA")
    somatic["Sample_ID"] = s
    return somatic
"""
Executes on import CPTAC statement. Selects files from docs folder in CPTAC package
utilizing DataFrameLoader from dataframe.py. Prints update as files are loaded into
dataframes.
"""
print("Loading Endometrial CPTAC data:")

dir_path = os.path.dirname(os.path.realpath(__file__))
data_directory = dir_path + os.sep + "Data" + os.sep

print("Loading Dictionary...")
dict = {}
file = open(data_directory + "definitions.txt", "r")

for line in file:
    line = line.strip()
    line = line.split("\t")
    dict[line[0]] = line[1]
file.close()

print("Loading Clinical Data...")
clinical_file_data = DataFrameLoader(data_directory + "clinical.txt").createDataFrame()
casesToDrop = clinical_file_data[clinical_file_data["Case_excluded"] == "Yes"].index
clinical_unfiltered = clinical_file_data[[
    'Proteomics_Participant_ID', 'Case_excluded',  'Proteomics_Tumor_Normal',  'Country',
    'Histologic_Grade_FIGO', 'Myometrial_invasion_Specify', 'Histologic_type', 'Treatment_naive', 'Tumor_purity',
    'Path_Stage_Primary_Tumor-pT', 'Path_Stage_Reg_Lymph_Nodes-pN', 'Clin_Stage_Dist_Mets-cM', 'Path_Stage_Dist_Mets-pM',
    'tumor_Stage-Pathological', 'FIGO_stage', 'LVSI', 'BMI', 'Age', 'Diabetes', 'Race', 'Ethnicity', 'Gender', 'Tumor_Site',
    'Tumor_Site_Other', 'Tumor_Focality', 'Tumor_Size_cm',   'Num_full_term_pregnancies']]
clinical_unfiltered = clinical_unfiltered.rename(columns={"Proteomics_Participant_ID":"Patient_ID"})
clinical = clinical_unfiltered.drop(casesToDrop, errors = "ignore") #Drops all samples with Case_excluded == Yes
clinical = clinical.drop(['Case_excluded'], axis=1)
clinical_unfiltered.name = "clinical"
clinical.name = clinical_unfiltered.name
derived_molecular_u = clinical_file_data.drop(['Proteomics_Participant_ID', 'Case_excluded',  'Proteomics_Tumor_Normal',  'Country',
    'Histologic_Grade_FIGO', 'Myometrial_invasion_Specify', 'Histologic_type', 'Treatment_naive', 'Tumor_purity',
    'Path_Stage_Primary_Tumor-pT', 'Path_Stage_Reg_Lymph_Nodes-pN', 'Clin_Stage_Dist_Mets-cM', 'Path_Stage_Dist_Mets-pM',
    'tumor_Stage-Pathological', 'FIGO_stage', 'LVSI', 'BMI', 'Age', 'Diabetes', 'Race', 'Ethnicity', 'Gender', 'Tumor_Site',
    'Tumor_Site_Other', 'Tumor_Focality', 'Tumor_Size_cm',   'Num_full_term_pregnancies', 
    'Proteomics_TMT_batch', 'Proteomics_TMT_plex', 'Proteomics_TMT_channel', 'Proteomics_Parent_Sample_IDs',
    'Proteomics_Aliquot_ID', 'Proteomics_OCT', 'WXS_normal_sample_type', 'WXS_normal_filename', 'WXS_normal_UUID', 'WXS_tumor_sample_type', 'WXS_tumor_filename',
    'WXS_tumor_UUID', 'WGS_normal_sample_type', 'WGS_normal_UUID', 'WGS_tumor_sample_type', 'WGS_tumor_UUID', 'RNAseq_R1_sample_type', 'RNAseq_R1_filename', 'RNAseq_R1_UUID',
    'RNAseq_R2_sample_type', 'RNAseq_R2_filename', 'RNAseq_R2_UUID', 'miRNAseq_sample_type', 'miRNAseq_UUID', 'Methylation_available', 'Methylation_quality'], axis=1)
derived_molecular = derived_molecular_u.drop(casesToDrop, errors = "ignore")
derived_molecular_u.name = "derived_molecular"
derived_molecular.name = derived_molecular_u.name
experimental_setup_u = clinical_file_data[['Proteomics_TMT_batch', 'Proteomics_TMT_plex', 'Proteomics_TMT_channel', 'Proteomics_Parent_Sample_IDs',
    'Proteomics_Aliquot_ID', 'Proteomics_OCT', 'WXS_normal_sample_type', 'WXS_normal_filename', 'WXS_normal_UUID', 'WXS_tumor_sample_type', 'WXS_tumor_filename',
    'WXS_tumor_UUID', 'WGS_normal_sample_type', 'WGS_normal_UUID', 'WGS_tumor_sample_type', 'WGS_tumor_UUID', 'RNAseq_R1_sample_type', 'RNAseq_R1_filename', 'RNAseq_R1_UUID',
    'RNAseq_R2_sample_type', 'RNAseq_R2_filename', 'RNAseq_R2_UUID', 'miRNAseq_sample_type', 'miRNAseq_UUID', 'Methylation_available', 'Methylation_quality']]
experimental_setup = experimental_setup_u.drop(casesToDrop, errors = "ignore")
experimental_setup_u.name = "experimental_setup"
experimental_setup.name = experimental_setup_u.name

print("Loading Acetylation Proteomics Data...")
acetylproteomics_u = DataFrameLoader(data_directory + "acetylproteomics.cct").createDataFrame()
acetylproteomics = acetylproteomics_u.drop(casesToDrop, errors = "ignore")
acetylproteomics.name = acetylproteomics_u.name

print("Loading Proteomics Data...")
proteomics_u = DataFrameLoader(data_directory + "proteomics.cct.gz").createDataFrame()
proteomics = proteomics_u.drop(casesToDrop, errors = "ignore")
proteomics.name = proteomics_u.name

print("Loading Transcriptomics Data...")
transcriptomics_u = DataFrameLoader(data_directory + "transcriptomics_linear.cct.gz").createDataFrame()
transcriptomics_u.name = "transcriptomics" # Instead of transcriptomics_linear generated by DataFrameLoader, to be more clear
transcriptomics_circular_u = DataFrameLoader(data_directory + "transcriptomics_circular.cct.gz").createDataFrame()
transcriptomics_circular_u.name = "circular_RNA" # Instead of transcriptomics_circular generated by DataFrameLoader, to be more clear
miRNA_u = DataFrameLoader(data_directory + "miRNA.cct.gz").createDataFrame()

transcriptomics = transcriptomics_u.drop(casesToDrop, errors = "ignore")
transcriptomics_circular = transcriptomics_circular_u.drop(casesToDrop, errors = "ignore")
miRNA = miRNA_u.drop(casesToDrop, errors = "ignore")

transcriptomics.name = transcriptomics_u.name
transcriptomics_circular.name = transcriptomics_circular_u.name
miRNA.name = miRNA_u.name

print("Loading CNA Data...")
cna_u = DataFrameLoader(data_directory + "CNA.cct.gz").createDataFrame()
cna = cna_u.drop(casesToDrop, errors = "ignore")
cna.name = cna_u.name

print("Loading Phosphoproteomics Data...")
phosphoproteomics_u = DataFrameLoader(data_directory + "phosphoproteomics_site.cct.gz").createDataFrame()
phosphoproteomics_u.name = "phosphoproteomics" # Instead of phosphoproteomics_site generated by DataFrameLoader, to avoid confusion
phosphoproteomics_gene_u = DataFrameLoader(data_directory + "phosphoproteomics_gene.cct.gz").createDataFrame()

phosphoproteomics = phosphoproteomics_u.drop(casesToDrop, errors = "ignore")
phosphoproteomics_gene = phosphoproteomics_gene_u.drop(casesToDrop, errors = "ignore")
phosphoproteomics.name = phosphoproteomics_u.name
phosphoproteomics_gene.name = phosphoproteomics_gene_u.name

print("Loading Somatic Mutation Data...")
somatic_binary_u = DataFrameLoader(data_directory + "somatic.cbt.gz").createDataFrame()
somatic_binary = somatic_binary_u.drop(casesToDrop, errors = "ignore")
somatic_binary.name = "somatic_mutation_binary"
somatic_mutation_u = DataFrameLoader(data_directory + "somatic.maf.gz").createDataFrame()
patient_ids = create_patient_ids(clinical_unfiltered) #maps C3L-**** number to S*** number
somatic_mutation_u = link_patient_ids(patient_ids, somatic_mutation_u) #adds S*** number to somatic mutations dataframe
somatic_mutation_u = somatic_mutation_u.set_index("Sample_ID")
somatic_mutation_u = somatic_mutation_u.drop(columns="Patient_Id")
somatic_mutation = somatic_mutation_u.drop(casesToDrop, errors = "ignore")
somatic_mutation.name = "somatic_mutation"

warning()
def list_data():
    """
    Parameters
    None

    Prints list of loaded data frames and dimensions

    Returns
    None
    """
    print("Below are the available endometrial data frames contained in this package:")
    data = [clinical, derived_molecular, experimental_setup, acetylproteomics, proteomics, transcriptomics, transcriptomics_circular, miRNA, cna, phosphoproteomics, phosphoproteomics_gene, somatic_binary, somatic_mutation]
    for dataframe in data:
        print("\t", dataframe.name)
        print("\t", "\t", "Dimensions:", dataframe.shape)
    #print("To find how to access the data, view the documentation with either list_api() or visit the github page with help().")

def list_api():
    """
    Parameters
    None

    Prints docstrings for all accessible functions

    Returns
    None
    """
    help(__name__)

def unfiltered_warning():
    """
    Parameters
    None

    Prints warning to about the unfiltered data

    Returns
    None
    """

    message = "IMPORTANT! Data has been filtered due to quality check on samples. Inclusion of unfiltered samples in analyses is NOT recommended."
    print(message)

def get_clinical(unfiltered=False):
    """
    Parameters
    unfiltered: boolean indicating whether to return unfiltered clinical data, aka clinical["Case_excluded"] == "Yes"

    Returns
    Clinical dataframe
    """
    if unfiltered:
        unfiltered_warning()
        return clinical_unfiltered
    return clinical

def get_derived_molecular(unfiltered=False):
    """
    Parameters
    unfiltered: boolean indicating whether to return unfiltered derived molecular data

    Returns
    Derived Molecular dataframe
    """
    if unfiltered:
        unfiltered_warning()
        return derived_molecular_u
    return derived_molecular

def get_experimental_setup(unfiltered=False):
    """
    Parameters
    unfiltered: boolean indicating whether to return unfiltered experimental setup data

    Returns
    Experimental Setup dataframe
    """
    if unfiltered:
        unfiltered_warning()
        return experimental_setup_u
    return experimental_setup

def get_acetylproteomics(unfiltered=False):
    """
    Parameters
    unfiltered: boolean indicating whether to return unfiltered acetylproteomics data

    Returns
    Acetylproteomics dataframe
    """
    if unfiltered:
        unfiltered_warning()
        return acetylproteomics_u
    return acetylproteomics

def get_proteomics(unfiltered=False):
    """
    Parameters
    unfiltered: boolean indicating whether to return unfiltered proteomics data

    Returns
    Proteomics dataframe
    """
    if unfiltered:
        unfiltered_warning()
        return proteomics_u
    return proteomics

def get_transcriptomics(unfiltered=False):
    """Gets transcriptomics dataframe.

    Parameters:
    unfiltered (bool, optional): Whether to include unfiltered samples. Default is false.

    Returns:
    pandas DataFrame: The transcriptomics dataframe.
    """
    if unfiltered:
        unfiltered_warning()
        return transcriptomics_u
    return transcriptomics

def get_circular_RNA(unfiltered=False):
    """Gets circular_RNA dataframe.

    Parameters:
    unfiltered (bool, optional): Whether to include unfiltered samples. Default is false.

    Returns:
    pandas DataFrame: The circular_RNA dataframe.
    """
    if unfiltered:
        unfiltered_warning()
        return transcriptomics_circular_u
    return transcriptomics_circular

def get_miRNA(unfiltered=False):
    """Gets miRNA dataframe.

    Parameters:
    unfiltered (bool, optional): Whether to include unfiltered samples. Default is false.

    Returns:
    pandas DataFrame: The miRNA dataframe.
    """
    if unfiltered:
        unfiltered_warning()
        return miRNA_u
    return miRNA

def get_CNA(unfiltered=False):
    """
    Parameters
    unfiltered: boolean indicating whether to return unfiltered CNA data

    Returns
    CNA dataframe
    """
    if unfiltered:
        unfiltered_warning()
        return cna_u
    return cna

def get_phosphoproteomics(unfiltered=False):
    """Gets the phosphoproteomics dataframe.

    Parameters:
    unfiltered (bool, optional): Whether to include unfiltered samples. Default is false.

    Returns:
    pandas DataFrame: The phosphoproteomics dataframe.
    """
    if unfiltered:
        unfiltered_warning()
        return phosphoproteomics_u
    return phosphoproteomics

def get_phosphoproteomics_gene(unfiltered=False):
    """Gets the phosphoproteomics_gene dataframe. The gene level phosphorylation measurement is an aggregate metric which potentially averages together individual measurements of different sites. Use get_phosphoproteomics() to view the data for individual sites.

    Parameters:
    unfiltered (bool, optional): Whether to include unfiltered samples. Default is false.

    Returns:
    pandas DataFrame: The phosphoproteomics_gene dataframe.
    """
    if unfiltered:
        unfiltered_warning()
        return phosphoproteomics_gene_u
    return phosphoproteomics_gene

def get_phosphosites(genes):
    """Returns dataframe with all phosphosites of specified gene or list of genes.

    Parameters:
    genes (str, or list or array-like of str): gene or list of genes to use to select phosphosites. str if single, list or array-like of str if multiple.

    Returns:
    pandas DataFrame: The phosphoproteomics for the specified gene(s).
    """
    return Utilities().get_omics_from_str_or_list(phosphoproteomics, genes)

def get_mutations(unfiltered=False):
    """Gets the somatic_mutation dataframe.

    Parameters:
    unfiltered (bool, optional): Whether to include unfiltered samples. Default is false.

    Returns:
    pandas DataFrame: The somatic_mutation dataframe.
    """
    if unfiltered:
        unfiltered_warning()
        return somatic_mutation_u
    return somatic_mutation

def get_mutations_binary(unfiltered=False):
    """Gets the somatic_mutation_binary dataframe, which has a binary value indicating, for each location on each gene, whether there was a mutation in that gene at that location, for each sample.

    Parameters:
    unfiltered (bool, optional): Whether to include unfiltered samples. Default is false.

    Returns:
    pandas DataFrame: The somatic_mutation_binary dataframe.
    """
    if unfiltered:
        unfiltered_warning()
        return somatic_binary_u
    return somatic_binary

def compare_omics(omics_df1, omics_df2, cols1=None, cols2=None):
    """Take specified column(s) from one omics dataframe, and append to specified columns(s) from another omics dataframe. Intersection (inner join) of indicies is used.

    Parameters:
    omics_df1 (pandas DataFrame): First omics dataframe to select columns from.
    omics_df2 (pandas DataFrame): Second omics dataframe to select columns from.
    cols1 (str, or list or array-like of str, optional): Column(s) to select from omics_df1. str if one key, list or array-like of str if multiple. Defaults to None, in which case we'll select the entire dataframe.
    cols2 (str, or list or array-like of str, optional): Column(s) to select from omics_df2. str if one key, list or array-like of str if multiple. Defaults to None, in which case we'll select the entire dataframe.

    Returns:
    pandas DataFrame: The selected columns from omics_df1 and omics_df2, merged into one dataframe.
    """
    # Make sure it's the right kind of dataframe
    valid_dfs = [
        'acetylproteomics',
        'proteomics',
        'transcriptomics', # But not circular_RNA or miRNA--they have incompatible column names.
        'CNA',
        'phosphoproteomics',
        'phosphoproteomics_gene']
    invalid = False
    if (omics_df1.name not in valid_dfs):
        invalid = True
        print("{} is not a valid dataframe for this function.".format(omics_df1.name))
    if (omics_df2.name not in valid_dfs):
        invalid = True
        print("{} is not a valid dataframe for this function.".format(omics_df2.name))
    if invalid:
        print("Valid dataframe options:")
        for df_name in valid_dfs:
            print('\t' + df_name)
        return

    # Return the merge.
    return Utilities().compare_omics(omics_df1, omics_df2, cols1, cols2)

def append_metadata_to_omics(metadata_df, omics_df, metadata_cols=None, omics_cols=None):
    """Joins columns from a metadata dataframe (clinical, derived_molecular, or experimental_setup) to part or all of an omics dataframe. Intersection (inner join) of indicies is used.

    Parameters:
    metadata_df (pandas DataFrame): Metadata dataframe to select columns from. Either clinical, derived_molecular, or experimental_setup.
    omics_df (pandas DataFrame): Omics dataframe to append the metadata columns to.
    metadata_cols (str, or list or array-like of str, optional): Column(s) to select from the metadata dataframe. str if one gene, list or array-like of str if multiple. Default is None, which will select the entire metadata dataframe.
    omics_cols (str, or list or array-like of str, optional): Column(s) to select from the omics dataframe. str if one gene, list or array-like of str if multiple. Default is None, which will select entire dataframe.

    Returns:
    pandas DataFrame: The selected metadata columns, merged with all or part of the omics dataframe.
    """
    # Make sure metadata_df is the right kind of dataframe
    valid_metadata_dfs = [
        'clinical',
        'derived_molecular',
        'experimental_setup']
    if (metadata_df.name not in valid_metadata_dfs):
        print("{} is not a valid dataframe for metadata_df parameter. Valid options:".format(metadata_df.name))
        for df_name in valid_metadata_dfs:
            print('\t' + df_name)
        return

    # Make sure omics_df is the right kind of dataframe
    valid_omics_dfs = [
        'acetylproteomics',
        'proteomics',
        'transcriptomics', # But not circular_RNA or miRNA--they have incompatible column names.
        'CNA',
        'phosphoproteomics',
        'phosphoproteomics_gene']
    if (omics_df.name not in valid_omics_dfs):
        print("{} is not a valid dataframe for omics_df parameter. Valid options:".format(omics_df.name))
        for df_name in valid_omics_dfs:
            print('\t' + df_name)
        return

    # Return the merge.
    return Utilities().append_metadata_to_omics(metadata_df, omics_df, metadata_cols, omics_cols)

def append_mutations_to_omics(omics_df, mutation_genes, omics_genes=None, show_location=True):
    """Select all mutations for specified gene(s), and appends them to all or part of the given omics dataframe. Intersection (inner join) of indicies is used. Each location or mutation cell contains a list, which contains the one or more location or mutation values corresponding to that sample for that gene, or a value indicating that the sample didn't have a mutation in that gene.

    Parameters:
    omics_df (pandas DataFrame): Omics dataframe to append the mutation data to.
    mutation_genes (str, or list or array-like of str): The gene(s) to get mutation data for. str if one gene, list or array-like of str if multiple.
    omics_genes (str, or list or array-like of str, optional): Gene(s) to select from the omics dataframe. str if one gene, list or array-like of str if multiple. Default will select entire dataframe.
    show_location (bool, optional): Whether to include the Locations column from the mutation dataframe. Defaults to True.

    Returns:
    pandas DataFrame: The mutations for the specified gene, appended to all or part of the omics dataframe. Each location or mutation cell contains a list, which contains the one or more location or mutation values corresponding to that sample for that gene, or a value indicating that the sample didn't have a mutation in that gene.
    """
    # Make sure omics_df is the right kind of dataframe
    valid_dfs = [
        'acetylproteomics',
        'proteomics',
        'transcriptomics', # But not circular_RNA or miRNA--they have incompatible column names.
        'CNA',
        'phosphoproteomics',
        'phosphoproteomics_gene']
    if (omics_df.name not in valid_dfs):
        print("{} is not a valid dataframe for omics_df parameter. Valid options:".format(omics_df.name))
        for df_name in valid_dfs:
            print('\t' + df_name)
        return

    # Return the merge.
    return Utilities().append_mutations_to_omics(somatic_mutation, omics_df, mutation_genes, omics_genes, show_location)

def define(term):
    """
    Parameters
    term: string of term to be defined

    Returns
    String definition of provided term
    """
    if term in dict:
        print(dict[term])
    else:
        print(term, "not found in dictionary. Alternatively, CPTAC.define() can be used to perform a web search of the term provided.")

def search(term):
    """
    Parameters
    term: string of term to be searched

    Performs online search of provided term

    Returns
    None
    """
    url = "https://www.google.com/search?q=" + term
    print("Searching for", term, "in web browser...")
    webbrowser.open(url)

def git_help():
    """
    Parameters
    None

    Opens github help page

    Returns
    None
    """
    print("Opening help.txt in web browser...")
    webbrowser.open("https://github.com/PayneLab/CPTAC/blob/master/doc/help.txt")

def embargo():
    """
    Parameters
    None

    Opens CPTAC embargo details in web browser

    Returns
    None
    """
    print("Opening embargo details in web browser...")
    webbrowser.open("https://proteomics.cancer.gov/data-portal/about/data-use-agreement")

def version():
    """
    Parameters
    None

    Prints version number of CPTAC package

    Returns
    Version number
    """
    version = {}
    with open(dir_path + os.sep + ".." + os.sep + "version.py") as fp: #.. required to navigate up to CPTAC folder from Endometrial folder, TODO: how to navigate from dataTest.py?
    	exec(fp.read(), version)
    return(version['__version__'])
