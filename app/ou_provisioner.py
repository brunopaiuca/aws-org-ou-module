#!/usr/bin/python
import json, boto3
from botocore.vendored import requests

#Initialize the status of the function
client = boto3.client(
    'organizations'
)

# Discover all children OUs
def discoverChildrenOf(_baseParents,_childType):

    discovered=[]

    for parent in _baseParents:

        discoveredChildren = []
        _discoverChildren_of_parentID = parent['Id']
        
        getChildren = get_children(_discoverChildren_of_parentID,_childType)

        discoveredChildren.extend(getChildren)
        enriched_discoveredChildren = enrich_ou_children(discoveredChildren)

        discovered.extend(enriched_discoveredChildren)

        for new_child in getChildren:
            
            searchChildren = get_children(new_child['Id'],_childType) 

            # If without children continue the search in the next items
            if searchChildren == []:
                continue
            
            # Add new Children to Loop 
            getChildren.extend(searchChildren)

            enriched_searchChildren = enrich_ou_children(searchChildren)
            discovered.extend(enriched_searchChildren)

    return discovered     
        

def get_org_structure(_startpointId, _childType):

    discoverChildren  = []
    children          = []

    # Get the Root OU Children
    _discoverChildren_of_parentID  = _startpointId
    discoveredChildrenBase         = get_children(_discoverChildren_of_parentID,_childType)
    enriched_discoveredChildren    = enrich_ou_children(discoveredChildrenBase)
    
    children.extend(enriched_discoveredChildren)
    children.extend(discoverChildrenOf(children,_childType))

    return children 


def enrich_ou_children(_children):

    enriched_children_array = []
    
    for _child in _children:

        OUID=_child['Id']
        OU_NAME=get_ou_param(OUID,'Name')
        ParentID=get_parents(OUID)

        _child['OUName']   = OU_NAME
        _child['ParentID'] = ParentID[0]['Id']

        enriched_children_array.append(_child)

    return enriched_children_array



def get_children(_parentId, _childType):
    
    children_resp=client.list_children (
       ParentId=_parentId,
       ChildType=_childType
    )

    children = children_resp['Children']
    return children

def get_parents(_childId):
    
    parents_resp=client.list_parents (
        ChildId=_childId
    )

    parents = parents_resp['Parents']

    return parents


def create_ou (ou_name, parent_id):

    orgUnitResponse=client.create_organizational_unit (
       ParentId=parent_id,
       Name=ou_name
    )

    OUID=str(orgUnitResponse['OrganizationalUnit']['Id'])
    return OUID


def get_ou_param(ou_id,param):
    
    orgUnitResponse = client.describe_organizational_unit(
        OrganizationalUnitId=ou_id
    )
    orgUnit = orgUnitResponse['OrganizationalUnit'][param]
    return orgUnit

# Check if I can create the OU inside the Parent
def check_creation_option (_parentId):

    # Get children list of Parent to check if this OU already exists
    checkChildren = get_children(_parentId,'ORGANIZATIONAL_UNIT')

    ret=0

    for v in checkChildren:
        
        # Get each Child Name to check
        _childName = get_ou_param(v['Id'],'Name')

        # If childname is equal OUName. The OU already exists so Break the Loop and do not create. 
        # Or else create the OU if the children is not equal the actual OUName

        if _childName == OUName:
            ret=0
            break

        else:
            ret=2
            continue
    else:
        ret=2

    return ret


with open('/srv/OU_Structure.json') as json_file:  
    data = json.load(json_file)
   
    for k, v in data.iteritems():
        if k == "topLevelOUID":
            topLevelOUID = v

    OU_STRUCTURE=get_org_structure(topLevelOUID,'ORGANIZATIONAL_UNIT')

    for k, v in data.iteritems():
        if k == "OUs":

            try:
                for ou in v:
                    
                    CREATE_OU=0
                    OUName   = ou['OUName']
                    
                    try:
                        ParentID = None
                        ParentOUName=ou['ParentOUName']
                    except:
                        ParentID=topLevelOUID
                    
                    # IF THE PARENT DOES NOT EXIST DONT CREATE
                    #if OU_STRUCTURE == [] and ParentID is not None:
                    if ParentID is not None:

                        CREATE_OU = check_creation_option(ParentID)

                        if CREATE_OU == 1 or CREATE_OU ==2:

                            print "Created OU: " + OUName + " Root OU."
                            OUID=create_ou(OUName,ParentID)
                            break

                    # If we already have structure
                    elif OU_STRUCTURE == [] and ParentID is None:
                        # Skip nas camadas inferiores enquanto nao ha topo  
                        continue  
                    
    
                    for parentOU in OU_STRUCTURE:
    
                        # If I dont have ParentID and I found the Parent in the Structure - For L2 L3 L4 and stuff
                        if ParentID is None and parentOU['OUName'] == ParentOUName:

                            ParentID  = parentOU['Id']
                            CREATE_OU = check_creation_option(ParentID)
    
                    if CREATE_OU == 1 or CREATE_OU == 2:
                                              
                        OUID=create_ou(OUName,ParentID)
                        print "Created OU: " + OUName + " in OU " + ParentOUName
                        break

            except Exception as e:
                print (e)
                print CREATE_OU
                print OUName
                print ParentID
