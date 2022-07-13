import yaml
import json
from edgeutils import ApiSession
import re
import os
import time

# Open Config File
with open('config.yaml') as f:
    config = yaml.safe_load(f)
    api = ApiSession(config)

## API ##

def getCollectionsApi():
    '''
    Calls API for collections and stores in collection_list
    '''
    global collection_list
    collection_list = api.get('collections')['content']

def getCollectionsLocal():
    '''
    Get collections from local JSON file, this will limit repeat calls during testing.
    '''
    global collection_list
    with open('JSON/my_collection.json') as f:
        collection_list = json.load(f)

def updateBase(update_list):
    '''
    Loops through contents of update_list and updates base segments.  This is called merge in the menu.
    Loop is delayed by one second for each update to limit API rate.
    '''
    for segment in update_list:
        api.put('collections/' + segment['id'], segment)
        print("Updated: {}".format(segment['name']))
        time.sleep(1)
    print()
    print("Update Operation Complete.")
    time.sleep(2)

def deleteDuplicate(delete_list):
    '''
    Loops through contents of delete_list and deletes duplicate segments.  This is called delete in the menu.
    Loop is delayed by one second for each update to limit API rate.
    '''
    for id in delete_list:
        delete_payload = ['{}'.format(id)]
        api.put('collections/bulk-delete', delete_payload)
        print("Deleted: {}".format(id))
        time.sleep(1)
    print()
    print("Delete Operation Complete.")
    time.sleep(2)

## Logic ##

def buildCollectionSets(collection_list):
    '''
    Filters collection_list for any segment that is "HOST_APP" type and matches the regex pattern "-\d+".
    All base segment names that have duplicates will be appended to "base_list".
    For each segment in "base_list" all duplicates with the same base name are appended to "duplicate_list".
    Sorts both lists.
    '''
 
    global base_list
    global duplicate_list

    # Clear lists at beginning to avoid duplication on rerun.
    base_list = []
    duplicate_list = []

    for collection in collection_list:
        if collection['query']['type'] == 'HOST_APP' and re.search(regex, collection['name']):
            
            # Append segments to base_list and duplicate_list without filter_list check.
            if not filter_list:
                duplicate_list.append(collection['name'])
                if collection['name'][:-2] not in base_list:
                    base_list.append(collection['name'][:-2])

            # Append segments to base_list and duplicate_list with filter_list check.
            elif filter_list and collection['name'][:-2] in filter_list:
                duplicate_list.append(collection['name'])
                if collection['name'][:-2] not in base_list:
                    base_list.append(collection['name'][:-2])

    base_list.sort()
    duplicate_list.sort()


def buildUpdateList(base_list, collection_list):
    '''
    Loop through collections and build list of segments that are members of base_list.  
    update_list will be used as the payload for the update call.
    '''

    global update_list
    update_list = []
    for collection in collection_list:
        if collection['name'] in base_list:
            update_list.append(collection)
                  
    for collection in collection_list:
        for segment in update_list:
            if segment['name'] in collection['name'] and segment['name'] != collection['name']:

                # append collection['query']['appNames'] to segment['query']['appNames'] if app names are not already in segment['query']['appNames']
                for app in collection['query']['appNames']:
                    if app not in segment['query']['appNames']:
                        segment['query']['appNames'].append(app)

                # append collection['query']['hosts'] to segment['query']['hosts'] if host names are not already in segment['query']['hosts']
                for host in collection['query']['hosts']:
                    if host not in segment['query']['hosts']:
                        segment['query']['hosts'].append(host)

                # append collection['query']['collectionsForHosts'] to segment['query']['collectionsForHosts'] if tags are not already in segment['query']['collectionsForHosts']
                for group in collection['query']['collectionsForHosts']:
                    if group not in segment['query']['collectionsForHosts']:
                        segment['query']['collectionsForHosts'].append(group)

                # append collection['query']['collectionsForApps'] to segment['query']['collectionsForApps'] if tags are not already in segment['query']['collectionsForApps']
                for group in collection['query']['collectionsForApps']:
                    if group not in segment['query']['collectionsForApps']:
                        segment['query']['collectionsForApps'].append(group)

def buildDeleteList(duplicate_list):
    '''
    Loop through collections and build list of segment IDs who are members of duplicate_list.  
    The list returned will be used as the payload for the bulk-delete call to remove the duplicate segments.
    '''
    global delete_list
    delete_list = []

    for collection in duplicate_list:
        for segment in collection_list:
            if collection == segment['name']:
                delete_list.append(segment['id'])


## Menu Functions ##


def printSearch():
    '''
    Prints display of all segments found with duplicate, if a filter_list is set, results are limited to filter_list.
    '''
    n = 1 
    print()
    if update_list:
        print()
        for segment in update_list:
            print("{}:".format(n))
            print(segment['name'])
            for duplicate in duplicate_list:
                if segment['name'] == duplicate[:-2]:
                    print(" > {}".format(duplicate))
            print()
            n += 1
        print()
        print("Search found {} application segment(s) that have one or more duplicates".format(len(update_list)))
        print()
    else:
        print()
        print("No duplicate application segments found...")
        print()
        print("Exiting application.")
        time.sleep(2)
        os.sys.exit()
        
def menuOptions():
    '''
    Prints menu options to screen.
    '''
    global filter_search
    print()
    print("--------Options----------")
    print()
    print("filter: '{}'".format(filter_search))
    print()
    print("1. Add text filter to search")
    print("2. Clear filter")
    print("3. Merge and delete")
    print("4. Merge only")
    print("5. Delete only")
    print("6. Quit")
    print("7. Diag")
    print()


def getSelection():
    '''
    Gets user selection from options menu.  Returns selection as string.   
    '''
    option_list = ['1', '2', '3', '4', '5', '6', '7']
    selection = input("Choose an option: 1 - 7\n")
    if selection in option_list:
        selection = selection
    else:
        print("Invalid input: Please type a number 1 - 7\n")
        getSelection()
    
    return selection

def filterReset():
    '''
    Reset filter_search to empty string.  Called when user selects option 2.
    '''
    global filter_search
    global filter_list
    filter_search = ''
    filter_list = []

# Used for testing and troubleshooting
def diagnostic():


    diag = True
    os.system('clear')
    
    while diag:
        '''
        Used for testing and troubleshooting.  Prints out all variables and their values.  Can be used to debug.  
        '''
        # Print all lists
        print("-----diagnostic-----")
        print()
        print('filter_list')
        print('len: ' + str(len(filter_list)))
        print(filter_list)
        print()
        print('base_list')
        print('len: ' + str(len(base_list)))
        print(base_list)
        print()
        print('duplicate_list')
        print('len: ' + str(len(duplicate_list)))
        print(duplicate_list)
        print()
        print('len of update_list')
        print(len(update_list))
        print()
        print('delete_list')
        print('len: ' + str(len(delete_list)))
        print(delete_list)
        print()

        # quit dianostic loop
        select = input('Type q to quit and update JSON/update_list...\n')
        if select == 'q':
            diag = False

    # Create JSON dir if not present
    if not os.path.exists('JSON'):
        os.makedirs('JSON')

    # Save update_list as JSON/update_list.json for easier viewing
    doc = json.dumps(update_list, indent=4)
    with open('JSON/update_list.json', 'w') as g:
        g.write(doc)
        g.close()


## Main Loop ##

def main():
    '''
    Main loop.  Prompts user for options and calls functions based on selection.
    '''
    run = True

    getCollectionsApi()

    while run:

        buildCollectionSets(collection_list)
        buildDeleteList(duplicate_list)
        buildUpdateList(base_list, collection_list)
        
        os.system('clear')
        printSearch()
        menuOptions()
        selection = getSelection()

        if selection == '1': # Populate filter_list 
            def getInput():
                global filter_search
                global filter_list
                os.system('clear')
                printSearch()
                print("---Set Filter---")
                filter_search = input('Type keyword or base segment name to filter search (Case Sensitive).  Type "exit" \n')
                for segment in base_list:
                    if filter_search in segment:
                        filter_list.append(segment)
                if not filter_list:
                    print("No matches found for '{}'".format(filter_search))
                    time.sleep(1)
                    getInput()
            
            getInput()

        elif selection == '2': # reset filter_list value
            filterReset()

        elif selection == '3': # call functions to update base segments and delete duplicate segments
            def getInput():
                os.system('clear')
                print()
                print("--------------Merge and Delete----------------")
                print()
                print("The following base segment(s) will be merged:")
                print()
                for segment in base_list:
                    print(" > {}".format(segment))
                print()
                print("The following duplicate segment(s) will be deleted:")
                print()
                for segment in duplicate_list:
                    print(" > {}".format(segment))    
                print()
                selection = input('Type "continue" to execute merge and delete operation, \nor "abort" to return to main menu: ')
                selection = selection.lower()
                
                if selection == "continue":
                    updateBase(update_list)
                    deleteDuplicate(delete_list)
                    filterReset()
                    main()

                elif selection == "abort":
                    pass

                else:
                    print()
                    print('Input not recognized. Type "continue" or "abort".')
                    time.sleep(2)
                    os.system('clear')
                    getInput()
            
            getInput()
            
        elif selection == '4': # call functions to merge base segments            
            def getInput():
                print()
                print("------------------Merge----------------------")
                print()
                print("The following base segment(s) will be merged:")
                print()
                for segment in base_list:
                    print(segment)       
                print()
                selection = input('Type "continue" to merge to base segment, or "abort" to return to main menu: ')
                selection = selection.lower()
                
                if selection == "continue":
                    updateBase(update_list)
                    filterReset()
                    main()

                elif selection == "abort":
                    pass
                    
                else:
                    print()
                    print('Input not recognized. Type "continue" or "abort".')
                    time.sleep(2)
                    os.system('clear')
                    getInput()
            
            getInput()
  
            
        elif selection == '5': # only delete duplicate segments.  This will not merge to original segment.
            def getInput():
                print()
                print("------------------Delete----------------------")
                print()
                print("The following duplicate segment(s) will be deleted:")
                print()
                for segment in duplicate_list:
                    print(segment)       
                print()
                selection = input('Type "continue" to delete duplicate segments, or "abort" to return to main menu: ')
                selection = selection.lower()
                
                if selection == "continue":
                    deleteDuplicate(delete_list)
                    filterReset()
                    main()

                elif selection == "abort":
                    pass

                else:
                    print()
                    print('Input not recognized. Type "continue" or "abort".')
                    time.sleep(2)
                    os.system('clear')
                    getInput()
            
            getInput()

        elif selection == '6': # Quit
            os.sys.exit()

        elif selection == '7': # Call diagnostic function
            diagnostic()


# Global vars
base_list = [] # track segment names that don't include "-#" (Base Segments)
duplicate_list = [] # track segment names that include "-#" (Duplicates)
regex = r'-\d+' # Used to match segments in collection_list that have "-#" appended to the end of the segment name
filter_search = '' # Input filter string from user
filter_list = [] # filters search to only include segments that match the filter_search text
collection_list = [] # list of collections of type "HOST_APP" and matching regex, returned by getCollections()
update_list = [] # List of dictionaries representing the total base segments returned in search. Used as payload for "Merge".
delete_list = [] # List of IDs for duplicate segments returned in search.  Used as payload for "Delete".

main()
        


