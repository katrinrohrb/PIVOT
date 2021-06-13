import matplotlib.pyplot as plt
import pandas as pd
import pdb
import math
import numpy as np

def get_article_names(data):
    return set(data["name"])
    
def get_article_targets_for_feature(data, feature, target):
    values = []
    for name in get_article_names(data):
        target_sum = data [(data["hypothesis"]==feature) & (data["name"]==name)][target].sum()
        values.append(target_sum)
        
    return np.array(values)

def get_article_impressions_for_feature(data, feature):
    return get_article_targets_for_feature(data, feature, "Impressions")

def make_histogram (data, title, filename, target, feature): 
        
    values = get_article_targets_for_feature(data, feature, target)/get_article_impressions_for_feature(data, feature)
    
    plt.hist(values)
    plt.title(feature+", "+target)

    #plt.savefig(filename)
    
def make_barchart(data, target, selection = None, features = ["h1","h2","h3"], feature_col="hypothesis", sort_by=None, color_by=None):
    if selection:
        for key, value in selection.items():
            data = data[(data[key]==value)]
    values = []
   
    for feature in features: 
        normalized_target_value = data [data[feature_col]==feature][target].sum()/data [data[feature_col]==feature]["Impressions"].sum()
        values.append(normalized_target_value)
    #pdb.set_trace()
    #sort values and features
    if sort_by == "target": 
        indices = np.argsort(values)
        features = [features[i] for i in indices]
        values = [values[i] for i in indices]
    plt.bar(features, values)
    plt.title(target)
    plt.ylabel(target + " per impressions")

def get_normalized_values(data,target, features = ["h1","h2","h3"], feature_col="hypothesis"):
    values = []
    for feature in features: 
        normalized_target_value = data [data[feature_col]==feature][target].sum()/data [data[feature_col]==feature]["Impressions"].sum()
        values.append(normalized_target_value)
    return values 

def make_multi_barchart(data, targets, selection, features = ["h1","h2","h3"], title=""):
    for key, value in selection.items():
        data = data[(data[key]==value)]
    for column in targets:
        
        values = get_normalized_values(data,column,features)
    
        plt.bar(features, values, label=column)
    plt.title(title)
    plt.legend()
    plt.ylabel("video watches per impressions")
    
 
def make_multi_histogram(data, target, features = ["h1","h2","h3"], title=None):
    if not title:
        title = target
    values = get_norm_hist_values(data,target)
    plt.hist(values, label=features)
    plt.legend()
    plt.title(title)
    plt.xlabel(target + " per impressions")
    plt.ylabel("number of articles")
    

def get_norm_hist_values(data,target,features = ["h1","h2","h3"]):
    values = []
    
    for feature in features:
        series = get_article_targets_for_feature(data, feature, target)/get_article_impressions_for_feature(data, feature)
        values.append(series)
    return np.array([[f1, f2, f3] for f1, f2, f3 in zip(*values)])
    
def clean_data_ads(data):

    #clean up data 
    #throw out some ads
    test = data["ad-name"]!="0"
    data = data[test]

    #throw out who is pivot ads
    test = ~data["ad-name"].str.contains("who_is_pivot")
    data = data[test]

    #throw out annonce ads 
    test = ~data["ad-name"].str.contains("annonce")
    data = data[test]

    #declare features and targets 
    features = "h1", "h2", "h3"

    targets_portrait = ['Impressions', 'Post shares', 'Post reactions', 'Post comments',
           'Link clicks', 'Post engagements', 'Landing page views']

    targets_video = targets_portrait + ['Three-second video views', 'Video watches at 50%',
           'Video watches at 75%', 'Video watches at 95%',
           'Video watches at 100%']

    #make new columns based on data encoded in ad name string 
    #is it a video? 
    is_video = data["ad-name"].str.contains("video")
    data["is_video"]= is_video

    #or is it a portrait?
    is_portrait = data["ad-name"].str.contains("portrait")
    data["is_portrait"]= is_portrait

    #find each entrepreneurs first and last name seperated by _
    split_ad_names = [string.split("-") for string in data["ad-name"]] 

    #create column for names
    names=[field[1] for field in split_ad_names]
    data["name"]= names

    #create column for language
    languages=[field[-1] for field in split_ad_names]
    data["language"] = languages

    #create column for hypothesis
    hypotheses=[field[2] for field in split_ad_names]
    data["hypothesis"]= hypotheses
    
    #create column for agegroup
    split_target = [string.split("-") for string in data["target"]]
    #print(set([len(field) for field in split_target]))
    age =[extract_age(field) for field in split_target]
    data["age"]= age
    
    return data

def read_clean_stories(data, filename, sheetname): 
    
    #read from file, with multiindex unfortunately
    story_chara_df=pd.read_excel(filename,sheetname,header=[0,1])

    #drop some columns
    story_chara_df=story_chara_df.drop(columns = ['Story written by', 'Story link',
           'Approved by Andrew (YES/NO)',
           'Stage (writing process/revisions/ready to be uploaded/uploaded)',
           'Stage (writing process/revisions/ready to be uploaded/uploaded)',
           'Date Published French'])
    
    #make naming of columns consistent (get rid of multiindex)
    new_columns=story_chara_df.columns.get_level_values(1).tolist()
    new_columns[1]=story_chara_df.columns.get_level_values(0)[1]
    story_chara_df.columns=new_columns
    
    #drop more columns
    story_chara_df=story_chara_df.drop(["Partner Affiliation","ID"], axis=1)
    
    #add column with names as they appear in fb ads excel sheet
    #to make selection easier
    matchnames_dict={}
    unfound_l=[]
    for sname in set(story_chara_df["SME name"]):
        selection = data["name"].str.contains(sname, case=False)
        result = set(data[selection]["name"])
        if len(result)!=1:
            unfound_l.append(sname)
        else: 
            lname = result.pop()
            matchnames_dict[sname]=lname

    #add the column
    story_chara_df["name"] = story_chara_df["SME name"].map(arg=matchnames_dict)
    
    #return a dataframe and list of names not appearing in fb ads excel sheet
    return story_chara_df, unfound_l

def extract_age(field):
    if len(field)==6:
        return field[4]+"-"+ field[5]
    return field[4]
   
