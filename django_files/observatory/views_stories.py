import json

import fpe

from django.core import serializers
from django.db.models import F, Q, Max
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import (HttpResponse)

from observatory.models import observastory, storychapter, observatoryuser
#object used to Encrypt/Decrypt
# 2014-06-16 mali: wtf is this?
###############################
fpe_obj = fpe.FPEInteger(key=b'mypetsnameeloise', radix=10, width=10)

#####################################
#create story
#####################################
def createStory(request):
       iscreatemode=True
       request.session['create']=iscreatemode
       #Get Current URL
       url = request.META['HTTP_REFERER']
       return redirect(url)

######################################
#save story
######################################
def endSaveStory(request):
  if request.POST["storyDetail"]:
   storyDetailJSON=request.POST["storyDetail"]
   objectJSON=json.loads(storyDetailJSON,encoding='utf-8')
   counter=0
   for counter in range(0,len(objectJSON)):
    data = objectJSON[counter]
    #Get story_name and story_desc
    storyName=data['storyName']
    storyDesc=data['storyDescription']
    #save story_name and story_desc to observastory table
    saveToStoryTable=observastory(story_name=storyName,story_desc=storyDesc)
    saveToStoryTable.save()
    storyId=observastory.objects.values_list('story_id',flat=True).filter(story_name=storyName).order_by('-story_id')[0:1]
    for story_id in storyId:
     request.session['storyId']=story_id
  if request.POST["storyChapterJSON"]:
   storyChapterJSON=request.POST["storyChapterJSON"]
   objectJSON = json.loads(storyChapterJSON,encoding='utf-8')
   chapterCount=len(objectJSON)
   storyId=request.session['storyId']
   updateChaptercount=observastory.objects.filter(story_id=storyId).update(number_of_chapters=chapterCount)
   counter=0
   for counter in range(0,len(objectJSON)):
    data = objectJSON[counter]
    #Get chapter_details
    chapterUrl=data['URL']
    chapterName=data['chapterName']
    chapterDescription=data['chapterDescription']
    chapterJs=json.dumps(data['JS'])
    prod_class= data['prod_class']
    language=data['language']
    #Get session parameters
    sessionParameters={}
    sessionParameters['product_classification']=prod_class
    sessionParameters['django_language']=language
    sessionParameters = json.dumps(sessionParameters)[1:-1]
    chapterSerialNo=counter+1
    #save session parameter and chapter details to storychapter table
    saveToChapterTable=storychapter(story_id=storyId,chapter_url=chapterUrl,chapter_title=chapterName,chapter_desc=chapterDescription,chapter_js_details=chapterJs,chapter_details=sessionParameters,serial_number=chapterSerialNo)
    saveToChapterTable.save()
  #check user in session
  if 'userid'  in request.session:
   storyId=request.session['storyId']
   userId=request.session['userid']
   updateUserId=observastory.objects.filter(story_id=storyId).update(user_id=userId)
  else:
   if request.POST["socialMediaIntegrationData"]:
    socialSitesDetails=request.POST["socialMediaIntegrationData"]
    jsonObjects=json.loads(socialSitesDetails,encoding='utf-8')
    index=0
    for index in range(0,len(jsonObjects)):
     data=jsonObjects[index]
     #Get socialmedia details
     email=data['email']
     name=data['name']
     request.session['username']=name
     source=data['source']
     #check user auth_type
     if source == 'google':
     #check useremail exits
      if observatoryuser.objects.filter(user_email=email).exists() == True:
       #Get userid
       getUserId=observatoryuser.objects.get(user_email=email)
       request.session['userid']=getUserId.user_id
       storyId=request.session['storyId']
       updateUserId=observastory.objects.filter(story_id=storyId).update(user_id=getUserId.user_id)
      else:
       #Create userid and get user id
       observaUser=observatoryuser(user_name=name,user_email=email,user_auth_type=source)
       observaUser.save()
       getUserId=observatoryuser.objects.get(user_email=email)
       request.session['userid']=getUserId.user_id
       storyId=request.session['storyId']
       updateUserId=observastory.objects.filter(story_id=storyId).update(user_id=getUserId.user_id)
     #check user auth_type
     if source == 'facebook':
      #check useremail exits
      if observatoryuser.objects.filter(user_email=email).exists() == True:
       #Get userid
       getUserId=observatoryuser.objects.get(user_email=email)
       request.session['userid']=getUserId.user_id
       storyId=request.session['storyId']
       updateUserId=observastory.objects.filter(story_id=storyId).update(user_id=getUserId.user_id)
      else:
       #Create userid and get user id
       observaUser=observatoryuser(user_name=name,user_email=email,user_auth_type=source)
       observaUser.save()
       getUserId=observatoryuser.objects.get(user_email=email)
       request.session['userid']=getUserId.user_id
       storyId=request.session['storyId']
       updateUserId=observastory.objects.filter(story_id=storyId).update(user_id=getUserId.user_id)
   else:
    storyId=request.session['storyId']
    #update publish value
    updatePublish=observastory.objects.filter(story_id=storyId).update(published=1)
  iscreatemode=False
  request.session['create']=iscreatemode
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return redirect(HTTP_HOST+'stories/')

#######################################
#browse story form
#######################################
def browseStoryForm(request):
    #check userid in session
    isbrowsemode=False
    request.session['retrieve']=isbrowsemode
    if 'userid'  in request.session:
     userUniqueId=request.session['userid']
    elif "socialMediaIntegrationData" in request.POST:
      socialSitesDetails=request.POST["socialMediaIntegrationData"]
      if socialSitesDetails:
       jsonObjects=json.loads(socialSitesDetails,encoding='utf-8')
       index=0
       for index in range(0,len(jsonObjects)):
        data=jsonObjects[index]
        #Get SocialMedia details
        email=data['email']
        name=data['name']
        request.session['username']=name
        source=data['source']
        #check user auth_type
        if source == 'google':
         #check useremail exits
         if observatoryuser.objects.filter(user_email=email).exists() == True:
          #Get userid
          getUserId=observatoryuser.objects.get(user_email=email)
      	  request.session['userid']=getUserId.user_id
         else:
	  #Create userid and Get userid
          observaUser=observatoryuser(user_name=name,user_email=email,user_auth_type=source)
          observaUser.save()
          getUserId=observatoryuser.objects.get(user_email=email)
          request.session['userid']=getUserId.user_id
        #check user auth_type
        if source == 'facebook':
         #check useremail exits
         if observatoryuser.objects.filter(user_email=email).exists() == True:
          #Get userid
          getUserId=observatoryuser.objects.get(user_email=email)
          request.session['userid']=getUserId.user_id
         else:
	  #Create userid and Get userid
          observaUser=observatoryuser(user_name=name,user_email=email,user_auth_type=source)
          observaUser.save()
          getUserId=observatoryuser.objects.get(user_email=email)
          request.session['userid']=getUserId.user_id
       userUniqueId=request.session['userid']
      else:
        userUniqueId=1
    else:
      userUniqueId=1
    #Username
    userName=request.session['username'] if 'username' in request.session else ""
    #Get Adminvalue
    checkAdmin=observatoryuser.objects.get(user_id=userUniqueId)
    checkAdmin=checkAdmin.isadmin
    #Get Mine story details
    dictMineStory={}
    dictMineStory=observastory.objects.values('story_name','story_id','published','featured','number_of_chapters').filter(user_id=userUniqueId).order_by('-story_id')
    for mineStory in dictMineStory:
     story_ids= mineStory['story_id']
     #encrypt story_id
     story_ids=int(story_ids)
     mineStory['story_id'] = fpe_obj.encrypt(story_ids)
    #Get Feature story details
    dictFeatureStory={}
    dictFeatureStory=observastory.objects.values('story_name','story_id','published','featured','number_of_chapters').filter(Q(featured=1) & (Q(published=1))).order_by('-story_id')
    for featureStory in dictFeatureStory:
     story_ids= featureStory['story_id']
     #encrypt story_id
     story_ids=int(story_ids)
     featureStory['story_id'] = fpe_obj.encrypt(story_ids)
    #Get Popular story details
    dictPopularStory={}
    dictPopularStory=observastory.objects.values('story_name','story_id','published','featured','number_of_chapters').filter(published=1).order_by('-likecount')[0:10]
    for popularStory in dictPopularStory:
     story_ids= popularStory['story_id']
     #encrypt story_id
     story_ids=int(story_ids)
     popularStory['story_id'] = fpe_obj.encrypt(story_ids)
    #Get Publish story details
    dictPublishStory={}
    dictPublishStory=observastory.objects.values('story_name','story_id','published','featured','number_of_chapters').filter(published=1).order_by('-story_id')
    for publishStory in dictPublishStory:
     story_ids= publishStory['story_id']
     #encrypt story_id
     story_ids=int(story_ids)
     publishStory['story_id'] = fpe_obj.encrypt(story_ids)
    return render_to_response('story/retrieveForm.html',{
        'publishStory':dictPublishStory,
	'checkAdmin':checkAdmin,
        'userName':userName,
	'userId':request.session['userid'] if 'userid' in request.session else 0,
	'mineStory':dictMineStory,
	'featureStory':dictFeatureStory,
	'popularStory':dictPopularStory},context_instance=RequestContext(request))

#######################################
#mine story list
#######################################
def minestory(request):
    userUniqueId=request.session['userid'] if 'userid' in request.session else 1
    #Get Mine story details
    dictMineStory=[]
    dictMineStory=observastory.objects.all().filter(user_id=userUniqueId).order_by('-story_id')
    serializeMineStory = serializers.serialize('json', dictMineStory)
    jsonMineStory=json.loads(serializeMineStory)
    for mineStory in jsonMineStory:
     story_ids= mineStory['pk']
     #encrypt story_id
     story_ids=int(story_ids)
     mineStory['pk'] = fpe_obj.encrypt(story_ids)
    jsonMineStory=json.dumps(jsonMineStory)
    return HttpResponse(jsonMineStory)

###########################################
#feature story list
###########################################
def featurestory(request):
 #Get Feature story details
    dictFeatureStory=[]
    dictFeatureStory=observastory.objects.all().filter(Q(featured=1) & (Q(published=1))).order_by('-story_id')
    serializeFeatureStory = serializers.serialize('json', dictFeatureStory)
    jsonFeatureStory= json.loads(serializeFeatureStory)
    for featureStory in jsonFeatureStory:
     story_ids= featureStory['pk']
     #encrypt story_id
     story_ids=int(story_ids)
     featureStory['pk'] = fpe_obj.encrypt(story_ids)
    jsonFeatureStory=json.dumps(jsonFeatureStory)
    return HttpResponse(jsonFeatureStory)

###########################################
#popular story list
###########################################
def popularstory(request):
 #Get Popular story details
    dictPopularStory=[]
    dictPopularStory=observastory.objects.all().filter(published=1).order_by('-likecount')[0:10]
    serializePopularStory = serializers.serialize('json', dictPopularStory)
    jsonPopularStory= json.loads(serializePopularStory)
    for popularStory in jsonPopularStory:
     story_ids=popularStory['pk']
     #encrypt story_id
     story_ids=int(story_ids)
     popularStory['pk']=fpe_obj.encrypt(story_ids)
    jsonPopularStory=json.dumps(jsonPopularStory)
    return HttpResponse(jsonPopularStory)

###########################################
#publish story list
###########################################
def publishstory(request):
#Get Publish story details
    dictPublishStory=[]
    dictPublishStory=observastory.objects.all().filter(published=1).order_by('-story_id')
    serializePublishStory = serializers.serialize('json', dictPublishStory)
    jsonPublishStory= json.loads(serializePublishStory)
    for publishStory in jsonPublishStory:
     story_ids= publishStory['pk']
     #encrypt story_id
     story_ids=int(story_ids)
     publishStory['pk']=fpe_obj.encrypt(story_ids)
    jsonPublishStory=json.dumps(jsonPublishStory)
    return HttpResponse(jsonPublishStory)
########################################
#end browse story
########################################
def endbrowsestory(request):
  #likebtn and isbrowsemode is false
  likeBtnEnable=False
  request.session['likeBtnEnable']=likeBtnEnable
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  #redirect to browse story page
  return redirect(HTTP_HOST+'stories/')

#######################################
# edit story form
#######################################
def editStoryForm(request,editStoryId):
  #Get editstoryid
  editStoryIdWithEncode=editStoryId
  #Decrypt edit storyid
  editStoryId = fpe_obj.decrypt(int(editStoryIdWithEncode))
  request.session['editStoryId']=editStoryId
  editStoryId=request.session['editStoryId']
  #Get story details
  stories=observastory.objects.values('story_name','story_desc','number_of_chapters').filter(story_id=editStoryId)
  #Get chapter details
  chapters = storychapter.objects.values('chapter_id','chapter_title','chapter_desc','serial_number').filter(story_id=editStoryId).order_by("serial_number")
  if storychapter.objects.filter(story_id=editStoryId).exists() == True:
   serialNumbers=storychapter.objects.filter(story_id=editStoryId).aggregate(Max('serial_number',flat=True))
   serialNumberTostring=(str(serialNumbers)[1:-1])
   serialNumberToArray = serialNumberTostring.split(':')[-1]
   serialNumber=serialNumberToArray.strip()
   updateNumberOfChapters=observastory.objects.filter(story_id=editStoryId).update(number_of_chapters=serialNumber)
  else:
   serialNumber=0
   #update number of chapter
   updateNumberOfChapters=observastory.objects.filter(story_id=editStoryId).update(number_of_chapters=serialNumber)
  temp={'storychapter':chapters,'observastory':stories}
  return render_to_response('story/editStoryForm.html',temp,context_instance=RequestContext(request))
############################################
# update story form
############################################
counter=0
def updateEditForm(request):
  storyId=request.session['editStoryId']
  #Get story title
  if "storyTitle" in request.POST:
   storyTitle=request.POST["storyTitle"]
  #Get story desc
  if "storyDesc" in request.POST:
   storyDesc=request.POST["storyDesc"]
  if request.POST["chapterJson"]:
   chapterJson=request.POST["chapterJson"]
   objs = json.loads(chapterJson,encoding='utf-8')
   global counter
   for counter in range(0,len(objs)):
    record = storychapter(chapter_title = objs[counter])
    data = objs[counter]
    #Get chapter details
    orderNumbder=data['order']
    chapterName=data['chapterTitle']
    chapterDesc= data['chapterDesc']
    chapterRemove=data['isRemoved']
    chapterID=data['chapterId']
    if chapterRemove == 'Y':
     #delete chapter
     deletechapter=storychapter.objects.filter(chapter_id=chapterID).delete()
    else:
     #Update edited chapter details
     chapters=storychapter.objects.filter(chapter_id=chapterID).update         (chapter_title=chapterName,chapter_desc=chapterDesc,serial_number=orderNumbder)
   counter += 1
  #Update edited story details
  story=observastory.objects.filter(story_id=storyId).update(story_name=storyTitle,story_desc=storyDesc)
  return redirect(HTTP_HOST+'stories/')
################################################
# publish
################################################
def published(request):
   isPublished=False
   #Get Story id
   browseStoryId=request.POST.get('storyId')
   #Decrypt story id
   browseStoryId=fpe_obj.decrypt(int(browseStoryId))
   #Get publish value
   browseStroyIdPublish=observastory.objects.values_list('published').filter(story_id=browseStoryId)
   for publishValue in browseStroyIdPublish:
    for value in publishValue:
     if value == 1:
      #Update publish value
      updatePublishValue=observastory.objects.filter(story_id=browseStoryId).update(published=0)
      isPublished=False
     else:
      #Update publish value
      updatePublishValue=observastory.objects.filter(story_id=browseStoryId).update(published=1)
      isPublished=True
   #Load in to json response
   json_response = {}
   json_response["isPublished"]=isPublished
   return HttpResponse(json.dumps(json_response))

#####################################################
# delete story
#####################################################
def deleteStory(request):
  #Check  user id in session
  if 'userid'  in request.session:
    #Get Story id
    deleteStoryId=request.POST.get('storyId')
    #Decrypt story id
    deleteStoryId=fpe_obj.decrypt(int(deleteStoryId))
    #Delete story in chapter table
    chapterIds=storychapter.objects.filter(story_id=deleteStoryId)
    if chapterIds is not None:
     deleteStory=storychapter.objects.filter(story_id=deleteStoryId).delete()
    #Delete story in story table
    deleteStory=observastory.objects.filter(story_id=deleteStoryId).delete()
    #Load in to json response
    json_response = {}
    json_response["storyId"]=deleteStoryId
    return HttpResponse(json.dumps(json_response))

################################################
# featured
################################################
def featured(request):
    isFeatured=False
    #Get Story id
    browseStoryId=request.POST.get('storyId')
    #Decrypt story id
    browseStoryId=fpe_obj.decrypt(int(browseStoryId))
    #Get featured value
    browseStroyIdFeature=observastory.objects.values_list('featured').filter(story_id=browseStoryId)
    for featureValue in browseStroyIdFeature:
     for value in featureValue:
      if value == 1:
       #Update featured value
       updateFeatureValue=observastory.objects.filter(story_id=browseStoryId).update(featured=0)
       isFeatured=False
      else:
       #Update featured value
       updateFeatureValue=observastory.objects.filter(story_id=browseStoryId).update(featured=1)
       isFeatured=True
    json_response = {}
    json_response["isFeatured"]=isFeatured
    return HttpResponse(json.dumps(json_response))
#################################################
# likecount
#################################################
def likeCount(request):
  #Get browse story id
  browseStoryId=request.session['browseStoryId'] if 'browseStoryIds' in request.session else 0
  #Increament like count
  updateLikeCount=observastory.objects.filter(story_id=browseStoryId).update(likecount=F('likecount')+1)
  likeBtnEnable=request.session['likeBtnEnable'] if 'likeBtnEnable' in request.session else False
  userId=request.session['userid'] if 'userid' in request.session else 0
  if userId > 0:
   #Save userid and story id to like table
   saveToLikeTable=observatory_like(user_id=userId,story_id=browseStoryId)
   saveToLikeTable.save()
  #Get like count
  story=observastory.objects.get(story_id=browseStoryId)
  request.session['likeCount']=story.likecount
  request.session['likeBtnEnable']=False
  json_response = {}
  json_response["likecount"]=request.session['likeCount']
  return HttpResponse(json.dumps(json_response))

####################################################
# logout
####################################################
def logout(request):
  #isbrowsemode and iscreatemode false
  iscreatemode=False
  request.session['create']=iscreatemode
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  #delete userid and username in session
  if 'userid' in request.session:
   del request.session['userid']
  if 'username' in request.session:
   del request.session['username']
  return redirect(HTTP_HOST+'explore/')

#####################################################
# end delete story
#####################################################
def cancelstory(request):
  #iscreatemode and isbrowsemode is false
  iscreatemode=False
  request.session['create']=iscreatemode
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  #Get current url
  url = request.META['HTTP_REFERER']
  return redirect(url)

############################################################
# browse story part
############################################################
browseArrayStoryId=0
browseModeIndex=0
def browsestories(request,browseStoryId):
  #Get browse storyid
  request.session['browseStoryId']=browseStoryId
  request.session['index']=0
  # isbrowsemode is true
  isbrowsemode=True
  request.session['retrieve']=isbrowsemode
  global browseModeIndex
  global browseArrayStoryId
  browseArrayStoryId = browseStoryId
  request.session['browseStoryIds']=browseStoryId
  userId=request.session['userid'] if 'userid' in request.session else 0
  #Get like count
  story=observastory.objects.get(story_id=browseStoryId)
  request.session['likeCount']=story.likecount
  #Like Btn
  if observatory_like.objects.filter(user_id=userId,story_id=browseStoryId).exists() == True:
    likeBtnEnable=False
    request.session['likeBtnEnable']=likeBtnEnable
  else:
     likeBtnEnable=True
     request.session['likeBtnEnable']=likeBtnEnable
  #Get storyname and story desc
  storyDetals=observastory.objects.get(story_id=browseStoryId)
  request.session['browseStoryName']=storyDetals.story_name
  request.session['browseStoryDesc']=storyDetals.story_desc
  #Get chapter ids and remove unicode
  browseStoryChapIds=storychapter.objects.values_list('serial_number', flat=True).filter(story_id=browseStoryId).order_by('serial_number')
  browseStoryChapIdsToSring=str(browseStoryChapIds)[1:-1]
  browseStoryChapIdsRemoveL=browseStoryChapIdsToSring.replace('L','')
  browseStoryChapIdsToArray=browseStoryChapIdsRemoveL.split(",")
  BrowseStoryChapNos= len(browseStoryChapIdsToArray)
  request.session['BrowseStoryChapNos']=BrowseStoryChapNos
  request.session['sessionBrowseStoryChapIds']=browseStoryChapIdsToArray
  browseStoryChapterIds=request.session['sessionBrowseStoryChapIds']
  if browseModeIndex < len(browseStoryChapterIds):
   if browseModeIndex == len(browseStoryChapterIds):
    browseModeIndex=0
  #Get sessions varibales
  chapterDetails=storychapter.objects.get(serial_number=browseStoryChapterIds[browseModeIndex],story_id=browseStoryId)
  browseStorySesVar=chapterDetails.chapter_details
  browseStorySesDataToArray=browseStorySesVar.split(',')
  for indexvar in range(0, len(browseStorySesDataToArray)):
   browseStorySessionData=browseStorySesDataToArray[indexvar].split(':')
   browseStorySesArrayLeft= browseStorySessionData[0]
   browseStorySesArrayRight= browseStorySessionData[1]
   sessionall=browseStorySesArrayLeft.strip()[1:-1]
   browseStorySesValues=browseStorySesArrayRight.strip()[1:-1]
   request.session[sessionall]=browseStorySesValues
   #Get chapter details
  request.session['browseStoryJScript']=chapterDetails.chapter_js_details
  request.session['browseStoryChapName']=chapterDetails.chapter_title
  request.session['browseStoryChapterDesc']=chapterDetails.chapter_desc
  chapterUrl=chapterDetails.chapter_url
  #Redirect chapter url
  return redirect(chapterUrl)
def viewStory(request,browseStoryId):
  #Get browse story id and decrypt story id
  browseStoryId=fpe_obj.decrypt(int(browseStoryId))
  return render_to_response('story/viewStory.html',{'browseStoryId':browseStoryId},context_instance=RequestContext(request))

####################################################################
# next browse story
####################################################################
def browseStoryNext(request):
  #Get browse story id
  browseStoryId=request.session['browseStoryIds']
  #Get Story name and desc
  storyDetals=observastory.objects.get(story_id=browseStoryId)
  request.session['browseStoryName']=storyDetals.story_name
  request.session['browseStoryDesc']=storyDetals.story_desc
  index=request.session['index']
  #Get chapter ids
  browseStoryChapIds=request.session['sessionBrowseStoryChapIds']
  browseStoryChapNos=len(browseStoryChapIds)
  request.session['BrowseStoryChapNos']=browseStoryChapNos
  if index < len(browseStoryChapIds):
   index=index+1
   if index == len(browseStoryChapIds):
    index=0
  #Get sessions varibales
  chapterDetails=storychapter.objects.get(serial_number=browseStoryChapIds[index],story_id=browseStoryId)
  request.session['index']=index
  browseStorySesVar=chapterDetails.chapter_details
  browseStorySesDataToArray=browseStorySesVar.split(',')
  for indexvar in range(0, len(browseStorySesDataToArray)):
   browseStorySessionData=browseStorySesDataToArray[indexvar].split(':')
   browseStorySesLeft= browseStorySessionData[0]
   browseStorySesRight= browseStorySessionData[1]
   sessionall=browseStorySesLeft.strip()[1:-1]
   browseStorySesValues=browseStorySesRight.strip()[1:-1]
   request.session[sessionall]=browseStorySesValues
  #Get chapter details
  request.session['browseStoryJScript']=chapterDetails.chapter_js_details
  request.session['browseStoryChapName']=chapterDetails.chapter_title
  request.session['browseStoryChapterDesc']=chapterDetails.chapter_desc
  chapterUrl=chapterDetails.chapter_url
  #Redirect url
  return redirect(chapterUrl)
  browseStoryChapIds=[]
###########################################################
#prev browse story
###########################################################
def browseStoryPrev(request):
  #Get browse story id
  browseStoryId=request.session['browseStoryIds']
  #Get story name and story desc
  storyDetals=observastory.objects.get(story_id=browseStoryId)
  request.session['browseStoryName']=storyDetals.story_name
  request.session['browseStoryDesc']=storyDetals.story_desc
  index=request.session['index']
  #Get chapter ids
  browseStoryChapterIds=request.session['sessionBrowseStoryChapIds']
  browsestoryChapterNos=len(browseStoryChapterIds)
  request.session['BrowseStoryChapNos']=browsestoryChapterNos
  if index < len(browseStoryChapterIds):
   if index  <= 0:
    index=len(browseStoryChapterIds)
   index=index-1
   request.session['index']=index
  #Get sessions varibales
  chapterDetails=storychapter.objects.get(serial_number=browseStoryChapterIds[index],story_id=browseStoryId)
  browseStorySesVar=chapterDetails.chapter_details
  request.session['index']=index
  browseStorySesDataToArray=browseStorySesVar.split(',')
  for  indexvar in range(0, len(browseStorySesDataToArray)):
   browseStorySessionData=browseStorySesDataToArray[indexvar].split(':')
   browseStorySesDataLeft= browseStorySessionData[0]
   browseStorySesDataRight= browseStorySessionData[1]
   sessionall=browseStorySesDataLeft.strip()[1:-1]
   browseStorySesValues=browseStorySesDataRight.strip()[1:-1]
   request.session[sessionall]=browseStorySesValues
  #Get chapter details
  request.session['browseStoryJScript']=chapterDetails.chapter_js_details
  request.session['browseStoryChapName']=chapterDetails.chapter_title
  request.session['browseStoryChapterDesc']=chapterDetails.chapter_desc
  #Redirect url
  chapterUrl=chapterDetails.chapter_url
  return redirect(chapterUrl)


def endbrowse(request):
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return redirect(HTTP_HOST+'explore/')


def generate_png( request ):
  import rsvg
  import cairo
  import cairosvg

  content = request.POST.get('svg_data')

  # Check if we have proper content first
  if ( content is not None ):
    # Fix the spaces etc and remove unwanted stuff from the content
    content = content.strip()
    content = content + "\n"

    #file_name="test"
    file_name="tree_map"

    #Now we want to write this to file
    svg_file = open( settings.DATA_FILES_PATH + "/" + file_name + ".svg", "w+" )
    svg_file.write( content )
    svg_file.close()

    # Read in the content
    svg_file = open( settings.DATA_FILES_PATH + "/" + file_name + ".svg", "r" )

    # Open up the file to be written to
    png_file = open( settings.DATA_FILES_PATH + "/" + file_name + ".png", "w+" )

    # Do the export
    cairosvg.svg2png( file_obj = svg_file, write_to = png_file )

    # Close the svg & png file
    svg_file.close()
    png_file.close()

    # Create the blank image surface
    #blank_surface = cairo.ImageSurface( cairo.FORMAT_ARGB32, 750, 480 )

    # Get the context
    #ctx = cairo.Context( blank_surface )

    # Dump SVG data to the image context
    #handler = rsvg.Handle( data = content.encode("utf-8") )
    #handler.render_cairo( ctx )

    # Create the final png image
    #final_png = blank_surface.write_to_png( settings.DATA_FILES_PATH + "/" + file_name + ".png" )

  return HttpResponse( "Success" )
