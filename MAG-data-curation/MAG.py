# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 06:05:03 2021

@author: lasse

## extended and edited by:
@author: victor
"""

from pyspark.sql import SparkSession
from pyspark.sql.types import *

class MicrosoftAcademicGraph(object):
  # constructor
  def __init__(self, spark, data_folderpath="/home/vicp/data/2021-08-02"):
    # AzureStorageAccess.__init__(self, container, account, sas, key) 
    self.data_folderpath = data_folderpath
    self.spark = spark

  datatypedict = {
    'bool' : BooleanType(),
    'int' : IntegerType(),
    'uint' : IntegerType(),
    'long' : LongType(),
    'ulong' : LongType(),
    'float' : FloatType(),
    'string' : StringType(),
    'DateTime' : DateType(),
  }

  # return stream schema
  def getSchema(self, streamName):
    schema = StructType()
    for field in self.streams[streamName][1]:
      fieldname, fieldtype = field.split(':')
      nullable = fieldtype.endswith('?')
      if nullable:
        fieldtype = fieldtype[:-1]
      schema.add(StructField(fieldname, self.datatypedict[fieldtype], nullable))
    return schema

  # return stream dataframe
  def getDataframe(self, streamName):

    df = self.spark.read.format('csv').options(header='false', delimiter='\t').schema(self.getSchema(streamName))\
           .load(self.data_folderpath + self.streams[streamName][0])
    # create temporary view for streamName
    df.createOrReplaceTempView(streamName)
    return df

  def getSubset(self, streamName, columns):
    df = self.getDataframe(streamName)
    # select subset of columns
    df = df.select(columns)
    return df 

  def saveFile(self, df, folderName, fileName): 
    destination = f"/home/vicp/data/2021-08-02/{folderName}/{fileName}"
    df.write.option("sep", "\t").option("encoding", "UTF-8")\
    .csv(destination)

  def query_sql(self, query):
    """ 
    Executes Spark SQL query and returns DataFrame with results.
    Assumes views are created prior to execution
    """
    df = self.spark.sql(query)
    return df

  # define stream dictionary
  streams = {
    'Affiliations' : ('mag/Affiliations.txt', ['AffiliationId:long', 'Rank:uint', 'NormalizedName:string', 'DisplayName:string', 'GridId:string', 'OfficialPage:string', 'WikiPage:string', 'PaperCount:long', 'PaperFamilyCount:long', 'CitationCount:long', 'Iso3166Code:string', 'Latitude:float?', 'Longitude:float?', 'CreatedDate:DateTime']),
    'AuthorExtendedAttributes' : ('mag/AuthorExtendedAttributes.txt', ['AuthorId:long', 'AttributeType:int', 'AttributeValue:string']),
    'Authors' : ('mag/Authors.txt', ['AuthorId:long', 'Rank:uint', 'NormalizedName:string', 'DisplayName:string', 'LastKnownAffiliationId:long?', 'PaperCount:long', 'PaperFamilyCount:long', 'CitationCount:long', 'CreatedDate:DateTime']),
    'ConferenceInstances' : ('mag/ConferenceInstances.txt', ['ConferenceInstanceId:long', 'NormalizedName:string', 'DisplayName:string', 'ConferenceSeriesId:long', 'Location:string', 'OfficialUrl:string', 'StartDate:DateTime?', 'EndDate:DateTime?', 'AbstractRegistrationDate:DateTime?', 'SubmissionDeadlineDate:DateTime?', 'NotificationDueDate:DateTime?', 'FinalVersionDueDate:DateTime?', 'PaperCount:long', 'PaperFamilyCount:long', 'CitationCount:long', 'Latitude:float?', 'Longitude:float?', 'CreatedDate:DateTime']),
    'ConferenceSeries' : ('mag/ConferenceSeries.txt', ['ConferenceSeriesId:long', 'Rank:uint', 'NormalizedName:string', 'DisplayName:string', 'PaperCount:long', 'PaperFamilyCount:long', 'CitationCount:long', 'CreatedDate:DateTime']),
    'EntityRelatedEntities' : ('advanced/EntityRelatedEntities.txt', ['EntityId:long', 'EntityType:string', 'RelatedEntityId:long', 'RelatedEntityType:string', 'RelatedType:int', 'Score:float']),
    'FieldOfStudyChildren' : ('advanced/FieldOfStudyChildren.txt', ['FieldOfStudyId:long', 'ChildFieldOfStudyId:long']),
    'FieldOfStudyExtendedAttributes' : ('advanced/FieldOfStudyExtendedAttributes.txt', ['FieldOfStudyId:long', 'AttributeType:int', 'AttributeValue:string']),
    'FieldsOfStudy' : ('advanced/FieldsOfStudy.txt', ['FieldOfStudyId:long', 'Rank:uint', 'NormalizedName:string', 'DisplayName:string', 'MainType:string', 'Level:int', 'PaperCount:long', 'PaperFamilyCount:long', 'CitationCount:long', 'CreatedDate:DateTime']),
    'Journals' : ('mag/Journals.txt', ['JournalId:long', 'Rank:uint', 'NormalizedName:string', 'DisplayName:string', 'Issn:string', 'Publisher:string', 'Webpage:string', 'PaperCount:long', 'PaperFamilyCount:long', 'CitationCount:long', 'CreatedDate:DateTime']),
    'PaperAbstractsInvertedIndex' : ('nlp/PaperAbstractsInvertedIndex.txt.{*}', ['PaperId:long', 'IndexedAbstract:string']),
    'PaperAuthorAffiliations' : ('mag/PaperAuthorAffiliations.txt', ['PaperId:long', 'AuthorId:long', 'AffiliationId:long?', 'AuthorSequenceNumber:uint', 'OriginalAuthor:string', 'OriginalAffiliation:string']),
    'PaperCitationContexts' : ('nlp/PaperCitationContexts.txt', ['PaperId:long', 'PaperReferenceId:long', 'CitationContext:string']),
    'PaperExtendedAttributes' : ('mag/PaperExtendedAttributes.txt', ['PaperId:long', 'AttributeType:int', 'AttributeValue:string']),
    'PaperFieldsOfStudy' : ('advanced/PaperFieldsOfStudy.txt', ['PaperId:long', 'FieldOfStudyId:long', 'Score:float']),
    'PaperMeSH' : ('advanced/PaperMeSH.txt', ['PaperId:long', 'DescriptorUI:string', 'DescriptorName:string', 'QualifierUI:string', 'QualifierName:string', 'IsMajorTopic:bool']),
    'PaperRecommendations' : ('advanced/PaperRecommendations.txt', ['PaperId:long', 'RecommendedPaperId:long', 'Score:float']),
    'PaperReferences' : ('mag/PaperReferences.txt', ['PaperId:long', 'PaperReferenceId:long']),
    'PaperResources' : ('mag/PaperResources.txt', ['PaperId:long', 'ResourceType:int', 'ResourceUrl:string', 'SourceUrl:string', 'RelationshipType:int']),
    'PaperUrls' : ('mag/PaperUrls.txt', ['PaperId:long', 'SourceType:int?', 'SourceUrl:string', 'LanguageCode:string']),
    'Papers' : ('mag/Papers.txt', ['PaperId:long', 'Rank:uint', 'Doi:string', 'DocType:string', 'PaperTitle:string', 'OriginalTitle:string', 'BookTitle:string', 'Year:int?', 'Date:DateTime?', 'OnlineDate:DateTime?', 'Publisher:string', 'JournalId:long?', 'ConferenceSeriesId:long?', 'ConferenceInstanceId:long?', 'Volume:string', 'Issue:string', 'FirstPage:string', 'LastPage:string', 'ReferenceCount:long', 'CitationCount:long', 'EstimatedCitation:long', 'OriginalVenue:string', 'FamilyId:long?', 'FamilyRank:uint?', 'CreatedDate:DateTime']),
    'RelatedFieldOfStudy' : ('advanced/RelatedFieldOfStudy.txt', ['FieldOfStudyId1:long', 'Type1:string', 'FieldOfStudyId2:long', 'Type2:string', 'Rank:float']),
    
    ### /WuSource
    # aggregated MAG (incl. disruption)
    'AggregatedMAG': ('WuSource/AggregatedMAG.txt', ['PaperId:long', 'Year:int?', 'FieldOfStudyId:long', 'TeamSize:int?', 'MultiInstitution:int?', 'CitationN:int?', 'D:float']),
    
    ### /Papers  
    # relevant columns for papers ONLY DocType = Journal OR Conference
    'papers_jc': ('Papers/papers_jc', ['PaperId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string']),
    # with FoS 
    'papers_FoS': ('Papers/papers_FoS', ['PaperId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'FieldOfStudyid:long']),
    # papers FS: FoS first now because we joined on this column.
    'papers_FS': ('Papers/papers_FS', ['FieldOfStudyId:long', 'PaperId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    # only in PaperAuthorAffiliation 
    'papers_paa': ('Papers/papers_paa', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    # only in PaperReferences (both columns) 
    'papers_ref_cite': ('Papers/papers_ref_cite', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    # PaperReferences (only between two valid papers) -> both ref&cite?
    'papers_references': ('Papers/papers_references', ['PaperId:long', 'PaperReferenceId:long']),
    # papers_unique (just the one column)
    'papers_unique': ('Papers/papers_unique', ['PaperId:long']),
    # meta_toplevel
    'meta_toplevel': ('Papers/meta_toplevel', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    # authors toplevel only & in meta/stuff. (created in PrepAuthorFoS)
    'author_FoS': ('Papers/author_FoS', ['PaperId:long', 'FieldOfStudyId:long', 'Year:int?', 'AuthorId:long']),

    ### /Subset (papers)

    # subset of papers_ref_cite: only those with DocType == "x"
    'meta_art': ('Subset/meta_art', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_biology': ('Subset/meta_biology', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_business': ('Subset/meta_business', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_chemistry': ('Subset/chemistry', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_computer': ('Subset/meta_computer', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_economics': ('Subset/meta_economics', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_engineering': ('Subset/meta_engineering', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_environmental': ('Subset/meta_environmental', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_geography': ('Subset/meta_geography', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_geology': ('Subset/meta_geology', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_history': ('Subset/meta_history', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_materials': ('Subset/meta_materials', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_mathematics': ('Subset/meta_mathematics', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_medicine': ('Subset/meta_medicine', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_philosophy': ('Subset/meta_philosophy', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_physics': ('Subset/meta_physics', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_political': ('Subset/meta_political', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_psychology': ('Subset/meta_psychology', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),
    'meta_sociology': ('Subset/meta_sociology', ['PaperId:long', 'FieldOfStudyId:long', 'DocType:string', 'FamilyId:long', 'Year:int?', 'PaperTitle:string', 'NormalizedName:string', 'Level:int?']),

    ### /Collaboration

    # all authors of papers in meta_toplevel
    'collaboration_toplevel': ('Collaboration/collaboration_toplevel', ['PaperId:long', 'AuthorId_r:long', 'AuthorId_l:long']),
    
    # collaboration
    
'collaboration_psychology': ('Collaboration/fields_toplevel/collaboration_psychology', ['PaperId:long', 'AuthorId_r:long', 'AuthorId_l:long']),
    'collaboration_biology': ('Collaboration/fields_toplevel/collaboration_biology', ['PaperId:long', 'AuthorId_r:long', 'AuthorId_l:long']),
    'collaboration_economics': ('Collaboration/fields_toplevel/collaboration_economics', ['PaperId:long', 'AuthorId_r:long', 'AuthorId_l:long']),
    'collaboration_sociology': ('Collaboration/fields_toplevel/collaboration_sociology', ['PaperId:long', 'AuthorId_r:long', 'AuthorId_l:long']),
    'collaboration_mathematics': ('Collaboration/fields_toplevel/collaboration_mathematics', ['PaperId:long', 'AuthorId_r:long', 'AuthorId_l:long']),

    ### /metrics
    'D_psych_nodouble': ('metrics/D_psych_nodouble', ['PaperId:long', 'D:float']), 

    #### old stuff

    'CollaborationPapers': ('Papersrocessed/CollaborationPrep.txt', ['PaperId:long', 'FieldOfStudyId:long', 'NormalizedName:string', 'AuthorId:long', 'Year:int?']),
    'PhysicsColaborationPrep': ('preprocessed/PhysicsColaborationPrep', ['PaperId:long', 'FieldOfStudyId:long', 'NormalizedName:string', 'AuthorId:long', 'Year:int?']),
    'ColabNetAll': ('networks/ColabNetAll', ['PaperId:long', 'AuthorId_l:long', 'AuthorId_r:long']),
    'CollabNetPhys': ('networks/CollabNetPhys', ['PaperId:long', 'AuthorId_l:long', 'AuthorId_r:long']),
    'Physics_1995_1999': ('subset/Physics_1995_1999', ['PaperId:long', 'AuthorId_l:long', 'AuthorId_r:long']),
    'Physics_2000_2004': ('subset/Physics_2000_2004', ['PaperId:long', 'AuthorId_l:long', 'AuthorId_r:long']),
    'Physics_2000': ('subset/Physics_2000', ['PaperId:long', 'AuthorId_l:long', 'AuthorId_r:long']),
    'Physics_2005': ('subset/Physics_2005', ['PaperId:long', 'AurhorId_l:long', 'AuthorId_r:long']),
    'physicsPapersNAuthors': ('metrics/physicsPapersNAuthords', ['PaperId:long', 'Nauthors:long', 'PaperTitle:string']),
    'Dphysics': ('disruption/Dphysics', ['PaperId:long', 'D:float']), 

    # old stuff

    'meta_paper': ('Papers/meta_paper', ['PaperId:long', 'DocType:string', 'NormalizedName:string', 'Year:int?', 'FamilyId:long?', 'AuthorN:long?']),
    'physics_meta': ('Papers/physics_meta', ['PaperId:long', 'DocType:string', 'NormalizedName:string', 'Year:int?', 'FamilyId:long?', 'AuthorN:long?']),
    'journals_meta': ('Papers/journals_meta', ['PaperId:long', 'DocType:string', 'NormalizedName:string', 'Year:int?', 'FamilyId:long?', 'AuthorN:long?']),
    'physics_journals_meta': ('Papers/physics_journals_meta', ['PaperId:long', 'DocType:string', 'NormalizedName:string', 'Year:int?', 'FamilyId:long?', 'AuthorN:long?']),
    'disruption_physics_journals': ('metrics/disruption_physics_journals', ['PaperId:long', 'D:float']),

    #### old try with disruption
    'disruption_double': ('metrics/disruption_double', ['PaperId:long', 'neu:int?', 'pro:int?', 'con:int?', 'r2r:int?', 'neuClean:int?', 'proClean:int?', 'D:float']),
    'disruption_nodouble': ('metrics/disruption_nodouble', ['PaperId:long', 'neu:int?', 'pro:int?', 'con:int?', 'r2r:int?', 'neuClean:int?', 'proClean:int?', 'D:float']),

	### LASSE NEW ###
'PaperAuthorAffiliationsUnique' : ('project/PaperAuthorAffiliationsUnique.txt', ['PaperId:long', 'AuthorId:long', 'MinAffiliationRank:long?']),
    'PaperRootField': ('project/PaperRootField.txt', ['PaperId:long', 'FieldOfStudyId:long', 'IsStem:int']),
    'StemAuthors2010': ('project/StemAuthors2010.txt', ['AuthorId:long', 'DisplayName:string', 'PaperFamilyCount:long', 'CitationCount:long', 'Gender:int']),
    'AuthorCountries': ('project/AuthorCountries.txt', ['AuthorId:long', 'DisplayName:string', 'Country:string?']),
    'ProjectPapers': ('project/ProjectPapers.txt', ['PaperId:long', 'FamilyId:long?', 'FieldOfStudyId:long', 'DocType:string?', 'Date:DateTime?', 'PubOrderInFamily:int', 'NumAuthors:int']),
    'GenderizedFirstnames': ('project/GenderizedSurnames.txt', ['Firstname:string', 'Country:string?', 'gender:string?', 'probability:float?', 'count:int?', 'genderized:int']),
    'AuthorsGenderized': ('project/AuthorsGenderized.txt', ['AuthorId:long', 'DisplayName:string', 'Country:string?', 'Gender:string?', 'Genderized:int?']),
    'AuthorScientificAge': ('project/AuthorScientificAge.txt', ['AuthorId:long', 'MinDateStem:DateTime?', 'MinDate:DateTime?']),
    'ProjectAuthors': ('project/ProjectAuthors.txt', ['AuthorId:long', 'DisplayName:string', 'Country:string?', 'Gender:string?', 'Genderized:int?', 'MinDate:DateTime?', 'MinDateStem:DateTime?']),
    'PaperAuthorAffiliationsAttributes': ('project/PaperAuthorAffiliationsAttributes.txt', ['PaperId:long', 'AuthorId:long', 'Date:DateTime?', 'Year:int?', 'Month:int?', 'Quarter:int?', 'Gender:int', 'ScientificAge:float?', 'CountryCode:string?']),

	### natcompandemic reproduce Lasse (sanity check) ### 

'ProjectAuthorsReproduce': ('natcompandemic/ProjectAuthorsReproduce.txt', ['AuthorId:long', 'DisplayName:string', 'Country:string?', 'Gender:string?', 'Genderized:int?', 'MinDate:DateTime?', 'MinDateStem:DateTime?']),

'PaperAuthorAffiliationsAttributesReproduce': ('natcompandemic/PaperAuthorAffiliationsAttributesReproduce.txt', ['PaperId:long', 'AuthorId:long', 'Date:DateTime?', 'Year:int?', 'Month:int?', 'Quarter:int?', 'Gender:int', 'ScientificAge:float?', 'CountryCode:string?']),

'AuthorScientificAgeReproduce': ('natcompandemic/AuthorScientificAgeReproduce.txt', ['AuthorId:long', 'MinDateStem:DateTime?', 'MinDate:DateTime?']),

'ProjectPapersReproduce': ('natcompandemic/ProjectPapersReproduce.txt', ['PaperId:long', 'FamilyId:long?', 'FieldOfStudyId:long', 'DocType:string?', 'Date:DateTime?', 'PubOrderInFamily:int', 'NumAuthors:int']),

### natcompandemic all doctypes (early preprocessing) ###

'ProjectAuthorsAllDocType': ('natcompandemic/ProjectAuthorsAllDocType.txt', ['AuthorId:long', 'DisplayName:string', 'Country:string?', 'Gender:string?', 'Genderized:int?', 'MinDate:DateTime?', 'MinDateStem:DateTime?']),

'PaperAuthorAffiliationsAttributesAllDocType': ('natcompandemic/PaperAuthorAffiliationsAttributesAllDocType.txt', ['PaperId:long', 'AuthorId:long', 'Date:DateTime?', 'Year:int?', 'Month:int?', 'Quarter:int?', 'Gender:int', 'ScientificAge:float?', 'CountryCode:string?']),

'AuthorScientificAgeAllDocType': ('natcompandemic/AuthorScientificAgeAllDocType.txt', ['AuthorId:long', 'MinDateStem:DateTime?', 'MinDate:DateTime?']),

'ProjectPapersAllDocType': ('natcompandemic/ProjectPapersAllDocType.txt', ['PaperId:long', 'FamilyId:long?', 'FieldOfStudyId:long', 'DocType:string?', 'Date:DateTime?', 'PubOrderInFamily:int', 'NumAuthors:int']),

### natcompandemic (needed subsets) ###

'PapersClean': ('natcompandemic/PapersClean.txt', ['PaperId:long']),
'Papers25': ('natcompandemic/Papers25.txt', ['PaperId:long']),
'PapersRefCite': ('natcompandemic/PapersRefCite.txt', ['PaperId:long']),

'AuthorsClean': ('natcompandemic/AuthorsClean.txt', ['AuthorId:long']),

'FoS': ('natcompandemic/FoS.txt', ['FieldOfStudyId:long', 'NormalizedName:string']), 

'ProjectPapersAll': ('natcompandemic/ProjectPapersAll.txt', ['PaperId:long', 'FieldOfStudyId:long','NormalizedName:string', 'DocType:string?', 'Date:DateTime?']),
'ProjectPapers25': ('natcompandemic/ProjectPapers25.txt', ['PaperId:long', 'FieldOfStudyId:long','NormalizedName:string', 'DocType:string?', 'Date:DateTime?']),
'ProjectPapersRefCite': ('natcompandemic/ProjectPapersRefCite.txt', ['PaperId:long', 'FieldOfStudyId:long','NormalizedName:string', 'DocType:string?', 'Date:DateTime?']),

'ProjectAuthorsAll': ('natcompandemic/ProjectAuthorsAll.txt', ['AuthorId:long', 'DisplayName:string', 'Country:string?', 'Gender:string?', 'Genderized:int?', 'MinDate:DateTime?']),

'PaperAuthorAffiliationsAttributesAll': ('natcompandemic/PaperAuthorAffiliationsAttributesAll.txt', ['PaperId:long', 'AuthorId:long', 'Date:DateTime?', 'Gender:int', 'ScientificAge:float?', 'CountryCode:string?', 'DocType:string?', 'FieldOfStudyId:long', 'NormalizedName:string']),
'PaperAuthorAffiliationsAttributes25': ('natcompandemic/PaperAuthorAffiliationsAttributes25.txt', ['PaperId:long', 'AuthorId:long', 'Date:DateTime?', 'Gender:int', 'ScientificAge:float?', 'CountryCode:string?', 'DocType:string?', 'FieldOfStudyId:long', 'NormalizedName:string']),
'PaperAuthorAffiliationsAttributesRefCite': ('natcompandemic/PaperAuthorAffiliationsAttributesRefCite.txt', ['PaperId:long', 'AuthorId:long', 'Date:DateTime?', 'Gender:int', 'ScientificAge:float?', 'CountryCode:string?', 'DocType:string?', 'FieldOfStudyId:long', 'NormalizedName:string']),
'PaperAuthorAffiliationsAttributesNoFilter': ('natcompandemic/PaperAuthorAffiliationsAttributesNoFilter.txt', ['PaperId:long', 'AuthorId:long', 'Date:DateTime?', 'Gender:int', 'ScientificAge:float?', 'CountryCode:string?', 'DocType:string?', 'FieldOfStudyId:long', 'NormalizedName:string']),

### repo ###

'ProjectPapersRepo': ('natcompandemic/ProjectPapersRepo.txt', ['PaperId:long', 'FieldOfStudyId:long', 'NormalizedName:string', 'Doctype:string?', 'Date:DateTime?']),

'PaperAuthorAffiliationsAttributesRepo': ('natcompandemic/PaperAuthorAffiliationsAttributesRepo.txt', ['PaperId:long', 'AuthorId:long', 'Date:DateTime?', 'Gender:int', 'ScientificAge:float?', 'CountryCode:string?', 'DocType:string?', 'FieldOfStudyId:long', 'NormalizedName:string']),

'PaperAuthorAffiliationsAttributesNoFilter': ('natcompandemic/PaperAuthorAffiliationsAttributesNoFilter.txt', ['PaperId:long', 'AuthorId:long', 'Date:DateTime?', 'Gender:int', 'ScientificAge:float?', 'CountryCode:string?', 'DocType:string?', 'FieldOfStudyId:long', 'NormalizedName:string']),


### natcompandemic (sanity checks) ###

'ProjectPapersRefCite': ('natcompandemic/ProjectPapersRefCite.txt', ['PaperId:long', 'FieldOfStudyId:long', 'NormalizedName:string', 'DocType:string?', 'Date:DateTime?']), 


'ProjectPapers25': ('natcompandemic/ProjectPapers25.txt', ['PaperId:long', 'FieldOfStudyId:long', 'NormalizedName:string', 'DocType:string?', 'Date:DateTime?']), 

}
