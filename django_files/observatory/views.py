# -*- coding: utf-8 -*-
# Django
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.core.urlresolvers import resolve
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils.translation import ungettext
from django.views.decorators.csrf import ensure_csrf_cookie
# General
import os
import collections
import base64
from django.db.models import F
from django.db.models import Q
import json
from django.core import serializers
from django.core.urlresolvers import reverse
# Project specific
from django.utils.translation import gettext as _
# App specific
from observatory.models import *
from observatory.models import storychapter
from observatory import helpers
from django.db.models import Max
from django.forms import ModelForm
import msgpack
import re
import fpe
# Import for cache
if settings.REDIS:
  from django.core.cache import cache, get_cache
  import redis
  import msgpack

if not settings.DB_PREFIX:
  DB_PREFIX = ''
else:
  DB_PREFIX = settings.DB_PREFIX

if not settings.VERSION:
  VERSION = '1.0.0'
else:
  VERSION = settings.VERSION

if not settings.HTTP_HOST:
  HTTP_HOST = '/'
else:
  HTTP_HOST = settings.HTTP_HOST

#object used to Encrypt/Decrypt
#####################################
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

def fluid(request):
  return render_to_response("fluid.html", context_instance=RequestContext(request))

###################
## Abandoned function? Does nothing.
###################
def new_ps(request):
  ps_nodes = Sitc4.objects.get_all("en")
  return render_to_response("new_ps.html", {"ps_nodes":json.dumps(ps_nodes, indent=2)},context_instance=RequestContext(request))

def home(request):
  iscreatemode=False
  request.session['create']=iscreatemode
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  import urllib2
  try:
    ip = request.META["HTTP_X_FORWARDED_FOR"]
  except KeyError:
    ip = request.META["REMOTE_ADDR"]
# Removed because causes issues when offline
#  url = "http://api.hostip.info/get_json.php?ip="+ip
#  json_response = json.loads(urllib2.urlopen(url).read())
#  country_code = json_response["country_code"]
#  try:
#    c = Country.objects.get(name_2char=country_code)
#  except Country.DoesNotExist:
    c = Country.objects.get(name_2char="us")
   # c = Country.objects.order_by('?')[0] # not all countries from this list can be used..
  return render_to_response("home.html",
    {"default_country": c},
    context_instance=RequestContext(request))

def about(request):
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return render_to_response("about/index.html", context_instance=RequestContext(request))
def support(request):
  return render_to_response("about/support.html", context_instance=RequestContext(request))
def research(request):
  return render_to_response("about/research.html", context_instance=RequestContext(request))
def glossary(request):
  return render_to_response("about/glossary.html", context_instance=RequestContext(request))
def team(request):
  return render_to_response("about/team.html", context_instance=RequestContext(request))
def data(request):
  return render_to_response("about/data.html", context_instance=RequestContext(request))
def permissions(request):
  return render_to_response("about/permissions.html", context_instance=RequestContext(request))
def privacy(request):
  return render_to_response("about/privacy.html", context_instance=RequestContext(request))

def about_data(request, data_type):
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  if data_type == "sitc4":
    items = [[getattr(x, "name_%s"% (lang,)), x.code] for x in Sitc4.objects.filter(community__isnull=False)]
    headers = ["Name", "SITC4 Code"]
    title = "SITC4 product names and codes"
  elif data_type == "hs4":
    items = [[x.name, x.code] for x in Hs4.objects.filter(community__isnull=False)]
    headers = ["Name", "HS4 Code"]
    title = "HS4 (harmonized system) product names and codes"
  elif data_type == "country":
    items = [[getattr(x, "name_%s"% (lang,)), x.name_3char] for x in Country.objects.filter(name_3char__isnull=False, name_2char__isnull=False, region__isnull=False)]
    headers = ["Name", "Alpha 3 Abbreviation"]
    title = "Country names and abbreviations"
  items.sort()
  return render_to_response("about/data.html",
    {"items":items, "headers":headers, "title": title},
    context_instance=RequestContext(request))

def api(request):
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return render_to_response("api/index.html", context_instance=RequestContext(request))

def api_apps(request):
  return render_to_response("api/apps.html", context_instance=RequestContext(request))

def api_data(request):
  return render_to_response("api/data.html", context_instance=RequestContext(request))

def book(request):
  isbrowsemode=False
  request.session['retrieve']=isbrowsemode
  return render_to_response("book/index.html", context_instance=RequestContext(request))

def set_language(request, lang):
  next = request.REQUEST.get('next', None)
  if not next:
    next = request.META.get('HTTP_REFERER', None)
  if not next:
    next = '/'
  response = HttpResponseRedirect(next)
  # if request.method == 'GET':
  #   lang_code = request.GET.get('language', None)
  lang_code = lang
  if lang_code:
    if hasattr(request, 'session'):
      request.session['django_language'] = lang_code
    else:
      response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
      translation.activate(lang_code)
  return response

def set_product_classification(request, prod_class):
  next = request.REQUEST.get('next', None)
  if not next:
    next = request.META.get('HTTP_REFERER', None)
  if not next:
    next = '/'
  response = HttpResponseRedirect(next)
  if prod_class:
    if hasattr(request, 'session'):
      request.session['product_classification'] = prod_class
      request.session['classification'] = prod_class
  return response

def download(request):
  try:
    import cairo, rsvg, xml.dom.minidom
  except:
    pass
  import csv
  #raise Exception(request.POST)
  content = request.POST.get("content")

  title = request.POST.get("title")

  format = request.POST.get("format")

  if format == "svg" or format == "pdf" or format == "png":
    svg = rsvg.Handle(data=content.encode("utf-8"))
    x = width = svg.props.width
    y = height = svg.props.height

  if format == "svg":
    response = HttpResponse(content.encode("utf-8"), mimetype="application/octet-stream")

  elif format == "pdf":
    response = HttpResponse(mimetype='application/pdf')
    surf = cairo.PDFSurface(response, x, y)
    cr = cairo.Context(surf)
    svg.render_cairo(cr)
    surf.finish()

  elif format == "png":
    response = HttpResponse(mimetype='image/png')
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, x, y)
    cr = cairo.Context(surf)
    svg.render_cairo(cr)
    surf.write_to_png(response)

  else:
    response = HttpResponse(mimetype="text/csv;charset=UTF-8")
    csv_writer = csv.writer(response, delimiter=',', quotechar='"')#, quoting=csv.QUOTE_MINIMAL)
    item_list = json.loads(content,encoding='utf-8')
    # raise Exception(content)
    for item in item_list:
      csv_writer.writerow([i.encode("utf-8") for i in item])

  # Need to change with actual title
  response["Content-Disposition"]= "attachment; filename=%s.%s" % (title, format)

  return response

def app(request, app_name, trade_flow, filter, year):
  # Get URL query parameters
  format = request.GET.get("format", False)
  lang = request.GET.get("lang", False)
  crawler = request.GET.get("_escaped_fragment_", False)

  country1, country2, product = None, None, None
  country1_list, country2_list, product_list, year1_list, year2_list, year_interval_list, year_interval = None, None, None, None, None, None, None

  trade_flow_list = ["export", "import", "net_export", "net_import"]

  year1_list = range(1962, 2011, 1)
  if "." in year:
    y = [int(x) for x in year.split(".")]
    year = range(y[0], y[1]+1, y[2])
    year2_list = year1_list
    year_interval_list = range(1, 11)
    year_interval = year[1] - year[0]
  else:
    year = int(year)

  json_response = {
    "year": year,
    "app": app_name
  }

  # Bilateral
  if "." in filter:
    bilateral_filters = filter.split(".")

    # Country x Product
    if len(bilateral_filters[1]) > 3:
      country1 = Country.objects.get(name_3char=bilateral_filters[0])
      product = Sitc4.objects.get(code=bilateral_filters[1])

      # Lists used for control pane
      country1_list = Country.objects.get_all(lang)
      product_list = Sitc4.objects.get_all(lang)
      trade_flow_list = ["export", "import"]

      article = "to" if trade_flow == "export" else "from"
      title = "Where did %s %s %s %s?" % (country1.name, trade_flow, product.name_en, article)

      # cspy means country1 / countr2 / show / year
      if crawler == "" or format == "json":
        json_response["data"] = Sitc4_ccpy.objects.cspy(country1, product, trade_flow)
        json_response["attr_data"] = Country.objects.get_all(lang)
        json_response["title"] = title

    # Country x Country
    else:
      country1 = Country.objects.get(name_3char=bilateral_filters[0])
      country2 = Country.objects.get(name_3char=bilateral_filters[1])

      # Lists used for control pane
      country1_list = Country.objects.get_all(lang)
      country2_list = country1_list
      trade_flow_list = ["export", "import"]

      article = "to" if trade_flow == "export" else "from"
      title = "What did %s %s %s %s?" % (country1.name, trade_flow, article, country2.name)

      # ccsy means country1 / countr2 / show / year
      if crawler == "" or format == "json":
        json_response["data"] = Sitc4_ccpy.objects.ccsy(country1, country2, trade_flow)
        json_response["attr_data"] = Sitc4.objects.get_all(lang)
        json_response["title"] = title

  # Product
  elif len(filter) > 3:
    product = Sitc4.objects.get(code=filter)
    product_list = Sitc4.objects.get_all(lang)

    title = "Who %ss %s?" % (trade_flow.replace("_", " "), product.name_en)

    # sapy means show / all / product / year
    if crawler == "" or format == "json":
      json_response["data"] = Sitc4_cpy.objects.sapy(product, trade_flow)
      json_response["attr_data"] = Country.objects.get_all(lang)
      json_response["title"] = title

  # Country
  else:
    country1 = Country.objects.get(name_3char=filter)
    country1_list = Country.objects.get_all(lang)

    title = "What did %s %s?" % (country1.name, trade_flow.replace("_", " "))

    # casy means country1 / all / show / year
    if crawler == "" or format == "json":
      json_response["data"] = Sitc4_cpy.objects.casy(country1, trade_flow)
      json_response["attr_data"] = Sitc4.objects.get_all(lang)
      json_response["title"] = title

  # Send data as JSON to browser via AJAX
  if format == "json":
    return HttpResponse(json.dumps(json_response))

  # Return page without visualization data
  return render_to_response("app/index.html", {
    "title": title,
    "trade_flow": trade_flow,
    "country1": country1,
    "country2": country2,
    "product": product,
    "year": year,
    "trade_flow_list": trade_flow_list,
    "country1_list": country1_list,
    "country2_list": country2_list,
    "product_list": product_list,
    "year1_list": year1_list,
    "year2_list": year2_list,
    "year_interval": year_interval,
    "year_interval_list": year_interval_list}, context_instance=RequestContext(request))

def app_redirect(request, app_name, trade_flow, filter, year):
  # Corrent for old spelling of tree map as one word
  if app_name == "treemap":
    app_name = "tree_map"

  # Bilateral
  if "." in filter:
    bilateral_filters = filter.split(".")

    # Country x Product
    if len(bilateral_filters[1]) > 3:
      country1, country2, product = bilateral_filters[0], "show", bilateral_filters[1]

    # Country x Country
    else:
      country1, country2, product = bilateral_filters[0], bilateral_filters[1], "show"

  # Product
  elif len(filter) > 3:
    country1, country2, product = "show", "all", filter

  # Country
  else:
    country1, country2, product = filter, "all", "show"
  # raise Exception("/explore/%s/%s/%s/%s/%s/%s/" % (app_name, trade_flow, country1, country2, product, year))
  return HttpResponsePermanentRedirect(HTTP_HOST+"explore/%s/%s/%s/%s/%s/%s/" % (app_name, trade_flow, country1, country2, product, year))

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

def explore(request, app_name, trade_flow, country1, country2, product, year="2011"):
  iscreatemode=False
  iscreatemode = request.session['create'] if 'create' in request.session else False
  isbrowsemode=False
  isbrowsemode = request.session['retrieve'] if 'retrieve' in request.session else False
  NoOfChapter=request.session['BrowseStoryChapNos'] if 'BrowseStoryChapNos' in request.session else ""
  browseStoryName=request.session['browseStoryName'] if 'browseStoryName' in request.session else ""
  browseStoryDesc=request.session['browseStoryDesc'] if 'browseStoryDesc' in request.session else ""
  browseChapterName=request.session['browseStoryChapName'] if 'browseStoryChapName' in request.session else ""
  browseChapterDesc=request.session['browseStoryChapterDesc'] if 'browseStoryChapterDesc'in request.session else ""
  browseModeJScript=request.session['browseStoryJScript'] if 'browseStoryJScript' in request.session else ""
  NoOfChpt=request.session['NoOfchap'] if 'NoOfchap' in request.session else ""
  userName=request.session['username'] if 'username' in request.session else ""
  userId=request.session['userid'] if 'userid' in request.session else 0
  likeBtnEnable=request.session['likeBtnEnable'] if 'likeBtnEnable' in request.session else False
  likeCount=request.session['likeCount'] if 'likeCount' in request.session else ""
  #Set app_name to session
  request.session['app_name']=app_name
  # raise Exception(country1, country2, product, year)
  # Get URL query parameters
  was_redirected = request.GET.get("redirect", False)
  crawler = request.GET.get("_escaped_fragment_", False)
  options = request.GET.copy()
  # set language (if session data available use that as default)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  options["lang"] = lang
  # set product classification (if session data available use that as default)
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("product_classification", prod_class)
  options["product_classification"] = prod_class
  options = options.urlencode()
  #Get session parameters
  language=lang
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()

  # Add prod class to request hash dictionary
  request_hash_dictionary['app_name'] = app_name
  request_hash_dictionary['lang'] = lang
  request_hash_dictionary['prod_class'] = prod_class

  # Add the arguments to the request hash dictionary
  request_hash_dictionary['trade_flow'] = trade_flow
  request_hash_dictionary['country1'] = country1
  request_hash_dictionary['country2'] = country2
  request_hash_dictionary['product_type'] = product
  request_hash_dictionary['year'] = year

  # We are here, so let us store this data somewhere
  request_hash_string = "_".join( request_hash_dictionary.values() )
  # Check staic image mode
  if( settings.STATIC_IMAGE_MODE == "PNG" ):
    # Check if we have a valid PNG image to display for this
    if os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".png"):
        # display the  static images
        displayviz = True
        displayImage = settings.STATIC_URL + "data/" + request_hash_string + ".png"
    else:
        displayviz=False
        displayImage = settings.STATIC_URL + "img/all/loader.gif"
  else:
    displayviz=False
    displayImage = settings.STATIC_URL + "img/all/loader.gif"

  # Verify countries from DB
  countries = [None, None]
  country_lists = [None, None]
  for i, country in enumerate([country1, country2]):
    if country != "show" and country != "all":
      try:
        countries[i] = Country.objects.get(name_3char=country)
        country_lists[i] = Country.objects.get_all(lang)
      except Country.DoesNotExist:
        alert = {"title": "Country could not be found",
          "text": "There was no country with the 3 letter abbreviateion <strong>%s</strong>. Please double check the <a href='about/data/country/'>list of countries</a>."%(country)}

  # The years of data available tends to vary based on the dataset used (Hs4
  # vs Sitc4) and the specific country.
  years_available_model = Sitc4_cpy if prod_class == "sitc4" else Hs4_cpy
  years_available = years_available_model.objects\
                         .values_list("year", flat=True)\
                         .order_by("year")\
                         .distinct()
  # Sometimes the query is not about a specific country (e.g. "all countries"
  # queries) in which case filtering by country is not necessary
  if countries[0]:
      years_available = years_available.filter(country=countries[0].id)
  # Force lazy queryset to hit the DB to reduce number of DB queries later
  years_available = list(years_available)

  country1_list, country2_list, product_list, year1_list, year2_list, year_interval_list, year_interval = None, None, None, None, None, None, None
  warning, alert, title = None, None, None
  data_as_text = {}
  # What is actually being shown on the page
  item_type = "product"

  # To make sure it cannot be another product class
  if prod_class != "hs4" and prod_class != "sitc4":
    prod_class = "sitc4"

  # Test for country exceptions
  if prod_class == "hs4":
    # redirect if and exception country
    if country1 == "bel" or country1 == "lux":
      return redirect(HTTP_HOST+'explore/%s/%s/blx/%s/%s/%s/?redirect=true' % (app_name, trade_flow, country2, product, year))
    if country1 == "bwa" or country1 == "lso" or country1 == "nam" or country1 == "swz":
      return redirect(HTTP_HOST+'explore/%s/%s/zaf/%s/%s/%s/?redirect=true' % (app_name, trade_flow, country2, product, year))
  if was_redirected:
    # display warning is redirected from exception
    if country1 == "blx":
      warning = {"title": "Country Substitution",
        "text": "In the Harmonized System (HS) classification, trade for Belgium and Luxembourg is reported as 'Belgium-Luxembourg'."}
    if country1 == "zaf":
      warning = {"title": "Country Substitution",
        "text": "In the Harmonized System (HS) classification, trade for Namibia, Republic of South Africa, Botswana, Lesotho and Swaziland is reported under 'South African Customs Union'."}

  trade_flow_list = [("export", _("Export")), ("import", _("Import")), ("net_export", _("Net Export")), ("net_import", _("Net Import"))]
  if (app_name == "product_space" or app_name == "rings"):
    trade_flow_list = [trade_flow_list[0]]

  year1_list = range(years_available[0], years_available[len(years_available)-1]+1, 1)

  if app_name == "stacked" and year == "2009":
    year = "1969.2011.10"

  if "." in year:
    y = [int(x) for x in year.split(".")]
    year_start = y[0]
    year_end = y[1]
    year2_list = year1_list
    year_interval_list = range(1, 11)
  else:
    year_start, year_end = None, None
    year = int(year)
    # Check that year is within bounds
    if year > years_available[len(years_available)-1]:
      year = years_available[len(years_available)-1]
    elif year < years_available[0]:
      year = years_available[0]

  api_uri = "api/%s/%s/%s/%s/%s/?%s" % (trade_flow, country1, country2, product, year, options)

  redesign_api_uri = "redesign/api/%s/%s/%s/%s/%s/%s" % (prod_class, trade_flow, country1, country2, product, year)

  country_code = None
  if country1 != "show" and country1 != "all": country_code = country1

  if crawler == "":
    view, args, kwargs = resolve("api/%s/%s/%s/%s/%s/" % (trade_flow, country1, country2, product, year))
    kwargs['request'] = request
    view_response = view(*args, **kwargs)
    raise Exception(view_response)
    data_as_text["data"] = view_response[0]
    data_as_text["total_value"] = view_response[1]
    data_as_text["columns"] = view_response[2]


  app_type = get_app_type(country1, country2, product, year)

  # Some countries need "the" before their names
  list_countries_the = set(("Cayman Islands", "Central African Republic",
                            "Channel Islands", "Congo, Dem. Rep.",
                            "Czech Republic", "Dominican Republic",
                            "Faeroe Islands", "Falkland Islands", "Fm Yemen Dm",
                            "Lao PDR", "Marshall Islands", "Philippines",
                            "Seychelles", "Slovak Republic",
                            "Syrian Arab Republic", "Turks and Caicos Islands",
                            "United Arab Emirates", "United Kingdom",
                            "Virgin Islands, U.S.", "United States"))
  if countries[0] and countries[0].name in list_countries_the:
    countries[0].name = "the "+countries[0].name

  #p_code, product = None, None
  if product not in ("show", "all"):
    p_code = product
    product = clean_product(p_code, prod_class)

  if not alert:

    # Generate page title depending on visualization being used
    trade_flow = trade_flow.replace('_', ' ')
    years = [] #TODO: implement
    product_name = product.name_en if not isinstance(product, basestring) else product
    country_names = [getattr(x, "name", None), for x in countries]
    title = helpers.get_title(app_name, app_type,
                              country_names=country_names,
                              trade_flow=trade_flow,
                              years=years,
                              product_name=product_name
                              )

    if app_type in ("ccsy", "cspy"):
      if _("net_export") in trade_flow_list: del trade_flow_list[trade_flow_list.index(_("net_export"))]
      if _("net_import") in trade_flow_list: del trade_flow_list[trade_flow_list.index(_("net_import"))]
      #trade_flow_list.pop(_("net_export"), None)

    # Should we show the product or partner tab pane?
    prod_or_partner = "partner" # quick fix should be merged with item_type
    if app_type in ["cspy", "sapy"]:
      prod_or_partner = "product"
    elif app_type == "casy":
      if app_name in ("stacked", "map", "tree_map"):
        prod_or_partner = "product"


  # Return page without visualization data

  # Making sure we return the product list every time
  if prod_class == "sitc4":
    product_list = Sitc4.objects.get_all(lang)
  else:
    product_list = Hs4.objects.get_all(lang)

  return render_to_response("explore/index.html", {
    "displayviz":displayviz,
    "displayImage":displayImage,
    "likeBtnEnable":likeBtnEnable,
    "browseModeJScript": browseModeJScript,
    "browseChapterDesc" : browseChapterDesc,
    "likeCount":likeCount,
    "browseChapterName": browseChapterName,
    "NoOfChapter" : NoOfChapter,
    "browseStoryName": browseStoryName,
    "browseStoryDesc" : browseStoryDesc,
    "isbrowsemode": isbrowsemode,
    "iscreatemode": iscreatemode,
    "userName":userName,
    "userId":userId,
    "language":language,
    "warning": warning,
    "alert": alert,
    "prod_class": prod_class,
    "data_as_text": data_as_text,
    "app_name": app_name,
    "title": title,
    "trade_flow": trade_flow,
    "country1": countries[0] or country1,
    "country2": countries[1] or country2,
    "product": product,
    "years_available": years_available,
    "year": year,
    "year_start": year_start,
    "year_end": year_end,
    "year1_list": year1_list,
    "year2_list": year2_list,
    "year_interval_list": year_interval_list,
    "trade_flow_list": trade_flow_list,
    "country1_list": country_lists[0],
    "country2_list": country_lists[1],
    "product_list": product_list,
    "api_uri": api_uri,
    "app_type": app_type,
    "redesign_api_uri": redesign_api_uri,
    "country_code": country_code,
    "prod_or_partner": prod_or_partner,
    "version": VERSION,
    "previous_page": request.META.get('HTTP_REFERER', None),
    "item_type": item_type}, context_instance=RequestContext(request))

def explore_random(request):
    """Pick a random country and explore that, for the /explore link on the top
    of the main template."""
    random_country = Country.objects.get_random().name_3char.lower()
    return HttpResponseRedirect(reverse('observatory.views.explore',
                                        args=('tree_map',
                                              'export',
                                              random_country,
                                              'all',
                                              'show',
                                              2012
                                              )))


'''attr_products / <PROD_CLASS>'''
def attr_products(request, prod_class):

  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)

  '''Grab extraneous details'''
  ## Classification & Django Data Call
  name = "name_%s" % lang

  # Get attribute information
  if prod_class == "sitc4":
    world_trade = list(Sitc4_py.objects.all().values('year','product_id','world_trade'))
    attr_list = list(Sitc4.objects.all().values('code',name,'id','color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'color':i['color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])

  elif prod_class == "hs4":
    world_trade = list(Hs4_py.objects.all().values('year','product_id','world_trade'))
    attr_list = list(Hs4.objects.all().values('code',name,'id','community_id__color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'item_id':i['id'],'color':i['community_id__color']}

  return HttpResponse(Sitc4.objects.get_all(lang) if prod_class == "sitc4" else Hs4.objects.get_all(lang))

'''<COUNTRY> / all / show / <YEAR>'''
def api_casy(request, trade_flow, country1, year):
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()

  # Store the country code
  country_code = country1
  '''Init variables'''
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  country1 = Country.objects.get(name_3char=country1)
  single_year = 'single_year' in request.GET

  '''Set query params with our changes'''
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  #Get app_name  from session
  app_name = request.session.get( "app_name", "tree_map" ) #request.session['app_name'] if 'app_name' in request.session else "tree_map"
  # See if we have an app name passed as part of the request URL
  forced_app_name = request.GET.get( "use_app_name", None )
  # If we have an app name passed, override and use that
  if ( forced_app_name is not None ):
      # override the app_name in this case, since generate_svg will pass app names specifically
      app_name = forced_app_name
  '''Grab extraneous details'''
  ## Clasification & Django Data Call
  name = "name_%s" % lang
  # Add prod class to request hash dictionary
  request_hash_dictionary['app_name'] = app_name
  request_hash_dictionary['lang'] = lang
  request_hash_dictionary['prod_class'] = prod_class

  # Add the arguments to the request hash dictionary
  request_hash_dictionary['trade_flow'] = trade_flow
  request_hash_dictionary['country'] = country_code

  # Set the product stuff based on the app
  if ( app_name in [ "product_space", "pie_scatter" ] ):
      request_hash_dictionary['product_type'] = 'all'
      request_hash_dictionary['product_display'] = 'show'
  else:
      request_hash_dictionary['product_type'] = 'show'
      request_hash_dictionary['product_display'] = 'all'
  request_hash_dictionary['year'] = year

  # We are here, so let us store this data somewhere
  request_hash_string = "_".join( request_hash_dictionary.values() ) #base64.b64encode( request_unique_hash )

  # Setup the store data
  store_data = request.build_absolute_uri().replace( "product_classification", "prod_class" ) + "||"
  store_page_url = request.build_absolute_uri().replace( "/api/", "/explore/" + app_name + "/" )
  store_page_url = store_page_url.replace( "data_type=json", "headless=true" )
  store_page_url = store_page_url.replace( "product_classification", "prod_class" )
  store_data = store_data + store_page_url + "||"
  store_data = store_data + request_hash_string

  # Write the store data to file
  store_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".store", "w+" )
  store_file.write( store_data )
  store_file.close()

  # Set proper permissions since we want the cron to remove the file as well
  os.chmod( settings.DATA_FILES_PATH + "/" + request_hash_string + ".store", 0777 )

  if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg" ) is True ):
    # Check the request data type
    if ( request.GET.get( 'data_type', None ) is None ):
      # Let us get the data from the file
      response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg", "r" )

      # Set the return data
      returnData = response_json_data.read()

      #"""Return to browser as JSON for AJAX request"""
      return HttpResponse( returnData )
    elif ( request.GET.get( 'data_type', '' ) == 'json' ):
      # Check if we have the valid json file
      if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ) is True ):
        # Let us get the data from the file
        response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "r" )

        # Set the return data
        returnData = response_json_data.read()

        #"""Return to browser as JSON for AJAX request"""
        return HttpResponse( returnData )

  # Get attribute information
  if prod_class == "sitc4":
    world_trade = list(Sitc4_py.objects.all().values('year','product_id','world_trade'))
    attr_list = list(Sitc4.objects.all().values('code',name,'id','color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'color':i['color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])

  elif prod_class == "hs4":
    world_trade = list(Hs4_py.objects.all().values('year','product_id','world_trade'))
    attr_list = list(Hs4.objects.all().values('code',name,'id','community_id__color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'item_id':i['id'],'color':i['community_id__color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])

  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()

  # Inflation adjustment
  magic = Cy.objects.filter(country=country1.id,
                            year__range=(years_available[0],
                                        years_available[-1])).values('year',
                                                                    'pc_constant',
                                                                    'pc_current',
                                                                    'notpc_constant')
  magic_numbers = {}
  for i in magic:
    magic_numbers[i['year']] = {"pc_constant":i['pc_constant'],
                                "pc_current":i['pc_current'],
                                "notpc_constant":i["notpc_constant"]}


  '''Define parameters for query'''
  if crawler == True or single_year == True:
    year_where = "AND cpy.year = %s" % (year,)
  else:
    year_where = " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "export_value - import_value as val"
    rca_col = "export_rca"
  elif trade_flow == "net_import":
    val_col = "import_value - export_value as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
    rca_col = "export_rca"
  else:
    val_col = "import_value as val"

  """Create query [year, id, abbrv, name_lang, val, export_rca]"""
  q = """
    SELECT cpy.year, p.id, p.code, p.name_%s, p.community_id, c.color,c.name, %s, %s, distance, opp_gain, py.pci
    FROM %sobservatory_%s_cpy as cpy, %sobservatory_%s as p, %sobservatory_%s_community as c, %sobservatory_%s_py as py
    WHERE country_id=%s and cpy.product_id = p.id %s and p.community_id = c.id and py.product_id=p.id and cpy.year=py.year
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, DB_PREFIX, prod_class, DB_PREFIX, prod_class, DB_PREFIX, prod_class, DB_PREFIX, prod_class, country1.id, year_where)

  """Prepare JSON response"""
  json_response = {}

  """Check cache"""
  if settings.REDIS:
    raw = redis.Redis("localhost")
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, "all", "show", prod_class, trade_flow)
    if single_year:
        key += ":%d" % int(year)
    # See if this key is already in the cache
    cache_query = raw.get(key)
    if (cache_query == None):

      rows = raw_q(query=q, params=None)
      total_val = sum([r[4] for r in rows])
      """Add percentage value to return vals"""
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[7], "rca":r[8],
             "distance":r[9],"opp_gain":r[10], "pci": r[11], "share": (r[7] / total_val)*100,
             "community_id": r[4], "color": r[5], "community_name":r[6], "code":r[2], "id": r[2]} for r in rows]

      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

      # SAVE key in cache.
      raw.set(key, msgpack.dumps(rows))#, 'data', json.dumps(rows))
      json_response["data"] = rows

    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded

  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[7] for r in rows])
    """Add percentage value to return vals"""
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[7], "rca":r[8],
             "distance":r[9],"opp_gain":r[10], "pci": r[11], "share": (r[7] / total_val)*100,
             "community_id": r[4], "color": r[5], "community_name":r[6], "code":r[2], "id": r[2]} for r in rows]

    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

    json_response["data"] = rows

  json_response["attr"] = attr
  json_response["attr_data"] = Sitc4.objects.get_all(lang) if prod_class == "sitc4" else Hs4.objects.get_all(lang)
  json_response["country1"] = country1.to_json()
  json_response["title"] = "What does %s %s?" % (country1.name, trade_flow.replace("_", " "))
  json_response["year"] = year
  json_response["item_type"] = "product"
  json_response["app_type"] = "casy"
  json_response["magic_numbers"] = magic_numbers
  json_response["world_trade"] = world_trade
  json_response["prod_class"] =  prod_class
  json_response["other"] = query_params

  if not os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ):
    response_json_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "w+" )
    response_json_file.write( json.dumps( json_response ) )
    response_json_file.close()

  # Check the request data type
  if ( request.GET.get( 'data_type', None ) is None ):
    return HttpResponse( "" )
  elif ( request.GET.get( 'data_type', '' ) == 'json' ):
    return HttpResponse(json.dumps(json_response))

def api_sapy(request, trade_flow, product, year):
  # Setup the hash dictionary
  #request_hash_dictionary = { 'trade_flow': trade_flow, 'product': product, 'year': year }
  """Init variables"""
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  product = clean_product(product, prod_class)
  #Set product code to product
  product_code = product.code
  """Set query params with our changes"""
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  #Get app_name from session
  app_name = request.session['app_name'] if 'app_name' in request.session else ""
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()
  # Add prod class to request hash dictionary
  request_hash_dictionary['app_name'] = app_name
  request_hash_dictionary['lang'] = lang
  request_hash_dictionary['prod_class'] = prod_class
  # Add the arguments to the request hash dictionary
  request_hash_dictionary['trade_flow'] = trade_flow
  request_hash_dictionary['country1'] =  'show'
  request_hash_dictionary['country2'] = 'all'
  request_hash_dictionary['product_dispaly'] = product_code
  request_hash_dictionary['year'] = year
  # We are here, so let us store this data somewhere
  request_hash_string = "_".join(request_hash_dictionary.values())

  # Setup the store data
  store_data = request.build_absolute_uri().replace( "product_classification", "prod_class" ) + "||"
  store_page_url = request.build_absolute_uri().replace( "/api/", "/explore/" + app_name + "/" )
  store_page_url = store_page_url.replace( "data_type=json", "headless=true" )
  store_page_url = store_page_url.replace( "product_classification", "prod_class" )
  store_data = store_data + store_page_url + "||"
  store_data = store_data + request_hash_string

  # Write the store data to file
  store_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".store", "w+" )
  store_file.write( store_data )
  store_file.close()


  if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg" ) is True ):
    # Check the request data type
    if ( request.GET.get( 'data_type', None ) is None ):
      # Let us get the data from the file
      response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg", "r" )

      # Set the return data
      returnData = response_json_data.read()

      #"""Return to browser as JSON for AJAX request"""
      return HttpResponse( returnData )
    elif ( request.GET.get( 'data_type', '' ) == 'json' ):
      # Check if we have the valid json file
      if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ) is True ):
        # Let us get the data from the file
        response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "r" )

        # Set the return data
        returnData = response_json_data.read()

        #"""Return to browser as JSON for AJAX request"""
        return HttpResponse( returnData )

  '''Grab extraneous details'''
  ## Clasification & Django Data Call
  name = "name_%s" % lang

  '''Grab extraneous details'''
  if prod_class == "sitc4":
    # attr_list = list(Sitc4.objects.all().values('code','name','color'))
    attr_list = list(Sitc4.objects.all().values('code',name,'id','color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'color':i['color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])
  elif prod_class == "hs4":
    # attr_list = list(Hs4.objects.all().values('code','name')) #.extra(where=['CHAR_LENGTH(code) = 2'])
    attr_list = list(Hs4.objects.all().values('code',name,'id','community_id__color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'item_id':i['id'],'color':i['community_id__color']}


  # Create dictionary of region codes
  region_list = list(Country_region.objects.all().values()) #.extra(where=['CHAR_LENGTH(code) = 2'])
  region = {}
  for i in region_list:
    region[i['id']] = i

  # Create dictinoary for continent groupings
  continent_list = list(Country.objects.all().distinct().values('continent'))
  continents = {}
  for i,k in enumerate(continent_list):
     continents[k['continent']] = i*1000

  """Define parameters for query"""
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "export_value - import_value as val"
    rca_col = "export_rca"
  elif trade_flow == "net_import":
    val_col = "import_value - export_value as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
    rca_col = "export_rca"
  else:
    val_col = "import_value as val"

  """Create query [year, id, abbrv, name_lang, val, export_rca]"""
  q = """
    SELECT year, c.id, c.name_3char, c.name_%s, c.region_id, c.continent, %s, %s
    FROM %sobservatory_%s_cpy as cpy, %sobservatory_country as c
    WHERE product_id=%s and cpy.country_id = c.id %s
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, DB_PREFIX, prod_class, DB_PREFIX, product.id, year_where)

  """Prepare JSON response"""
  json_response = {}

  """Check cache"""
  if settings.REDIS:
    # raw = get_redis_connection('default')
    raw = redis.Redis("localhost")
    key = "%s:%s:%s:%s:%s" % ("show", "all", product.id, prod_class, trade_flow)
    # See if this key is already in the cache
    cache_query = raw.get(key)
    if (cache_query == None):
      rows = raw_q(query=q, params=None)
      total_val = sum([r[6] for r in rows])
       # raise Exception(total_val)
      """Add percentage value to return vals"""
      # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
               "id": r[1], "region_id":r[4],"continent":r[5]} for r in rows]

      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

      json_response["data"] = rows

      # SAVE key in cache.
      raw.set(key, msgpack.dumps(rows))

    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded

  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[6] for r in rows])
    # raise Exception(total_val)
    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
             "id": r[1], "region_id":r[4],"continent":r[5]} for r in rows]

    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

    json_response["data"] = rows

  json_response["attr_data"] = Country.objects.get_all(lang)
  json_response["product"] = product.to_json()
  json_response["title"] = "Who %sed %s?" % (trade_flow.replace("_", " "), product.name_en)
  json_response["year"] = year
  json_response["item_type"] = "country"
  json_response["app_type"] = "sapy"
  json_response["attr"] = attr
  json_response["region"]= region
  json_response["continents"] = continents
  json_response["other"] = query_params

  if not os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ):
    response_json_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "w+" )
    response_json_file.write( json.dumps( json_response ) )
    response_json_file.close()

  # raise Exception(time.time() - start)
  # Check the request data type
  if ( request.GET.get( 'data_type', None ) is None ):
    #"""Return to browser as JSON for AJAX request"""
    return HttpResponse( "" )
  elif ( request.GET.get( 'data_type', '' ) == 'json' ):
    """Return to browser as JSON for AJAX request"""
    return HttpResponse(json.dumps(json_response))


'''<COUNTRY> / show / product / <YEAR>'''
def api_csay(request, trade_flow, country1, year):
  """Init variables"""
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  country1 = Country.objects.get(name_3char=country1)
  #Get app_name from session
  app_name = request.session['app_name'] if 'app_name' in request.session else ""
  """Set query params with our changes"""
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()
  # Add prod class to request hash dictionary
  request_hash_dictionary['app_name'] = app_name
  request_hash_dictionary['lang'] = lang
  request_hash_dictionary['prod_class'] = prod_class
  # Add the arguments to the request hash dictionary
  request_hash_dictionary['trade_flow'] = trade_flow
  request_hash_dictionary['country1'] =  country1.name_3char.lower()
  request_hash_dictionary['product_dispaly'] = 'show'
  request_hash_dictionary['country2'] = 'all'
  request_hash_dictionary['year'] = year

  # We are here, so let us store this data somewhere
  request_hash_string = "_".join(request_hash_dictionary.values())

  # Setup the store data
  store_data = request.build_absolute_uri().replace( "product_classification", "prod_class" ) + "||"
  store_page_url = request.build_absolute_uri().replace( "/api/", "/explore/" + app_name + "/" )
  store_page_url = store_page_url.replace( "data_type=json", "headless=true" )
  store_page_url = store_page_url.replace( "product_classification", "prod_class" )
  store_data = store_data + store_page_url + "||"
  store_data = store_data + request_hash_string

  # Write the store data to file
  store_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".store", "w+" )
  store_file.write( store_data )
  store_file.close()

  if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg" ) is True ):
    # Check the request data type
    if ( request.GET.get( 'data_type', None ) is None ):
      # Let us get the data from the file
      response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg", "r" )

      # Set the return data
      returnData = response_json_data.read()

      #"""Return to browser as JSON for AJAX request"""
      return HttpResponse( returnData )
    elif ( request.GET.get( 'data_type', '' ) == 'json' ):
      # Check if we have the valid json file
      if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ) is True ):
        # Let us get the data from the file
        response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "r" )

        # Set the return data
        returnData = response_json_data.read()

        #"""Return to browser as JSON for AJAX request"""
        return HttpResponse( returnData )
  '''Grab extraneous details'''
  region_list = list(Country_region.objects.all().values()) #.extra(where=['CHAR_LENGTH(code) = 2'])
  region = {}
  for i in region_list:
    region[i['id']] = i

  continent_list = list(Country.objects.all().distinct().values('continent'))
  continents = {}
  for i,k in enumerate(continent_list):
     continents[k['continent']] = i*1000

  """Define parameters for query"""
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "SUM(export_value - import_value) as val"
  elif trade_flow == "net_import":
    val_col = "SUM(import_value - export_value) as val"
  elif trade_flow == "export":
    val_col = "SUM(export_value) as val"
  else:
    val_col = "SUM(import_value) as val"

  '''Create query [year, id, abbrv, name_lang, val, rca]'''
  q = """
    SELECT year, c.id, c.name_3char, c.name_%s, c.region_id, c.continent, %s, %s
    FROM %sobservatory_%s_ccpy as ccpy, %sobservatory_country as c
    WHERE origin_id=%s and ccpy.destination_id = c.id %s
    GROUP BY year, destination_id
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, DB_PREFIX, prod_class, DB_PREFIX, country1.id, year_where)

  """Prepare JSON response"""
  json_response = {}

  """Check cache"""
  if settings.REDIS:
    raw = redis.Redis("localhost")
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, "show", "all", prod_class, trade_flow)
    # See if this key is already in the cache
    cache_query = raw.get(key)
    if (cache_query == None):
      rows = raw_q(query=q, params=None)
      total_val = sum([r[6] for r in rows])

      """Add percentage value to return vals"""
      # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
               "id":r[1], "region_id":r[4], "continent":r[5]} for r in rows]

      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

      json_response["data"] = rows

      # SAVE key in cache.
      raw.set(key, msgpack.dumps(rows))

    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded

  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[6] for r in rows])

    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
             "id":r[1], "region_id":r[4], "continent":r[5]} for r in rows]

    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

    json_response["data"] = rows

  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()

  magic = Cy.objects.filter(country=country1.id,
                            year__range=(years_available[0],
                                        years_available[-1])).values('year',
                                                                     'pc_constant',
                                                                     'pc_current',
                                                                     'notpc_constant')
  magic_numbers = {}
  for i in magic:
    magic_numbers[i['year']] = {"pc_constant":i['pc_constant'],
                                  "pc_current":i['pc_current'],
                                  "notpc_constant":i["notpc_constant"]}

  """Set article variable for question """
  article = "to" if trade_flow == "export" else "from"

  json_response["attr_data"] = Country.objects.get_all(lang)
  json_response["country1"] = country1.to_json()
  json_response["title"] = "Where does %s %s %s?" % (country1.name, trade_flow, article)
  json_response["year"] = year
  json_response["item_type"] = "country"
  json_response["app_type"] = "csay"
  json_response["region"]= region
  json_response["continents"]= continents
  json_response["prod_class"] =  prod_class
  json_response["magic_numbers"] = magic_numbers
  json_response["other"] = query_params

  # raise Exception(time.time() - start)
  # Check the request data type
  if ( request.GET.get( 'data_type', None ) is None ):
    #"""Return to browser as JSON for AJAX request"""
    return HttpResponse( "" )
  elif ( request.GET.get( 'data_type', '' ) == 'json' ):
    """Return to browser as JSON for AJAX request"""
    return HttpResponse(json.dumps(json_response))


def api_ccsy(request, trade_flow, country1, country2, year):
  # import time
  # start = time.time()
  '''Init variables'''
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  country1 = Country.objects.get(name_3char=country1)
  country2 = Country.objects.get(name_3char=country2)
  article = "to" if trade_flow == "export" else "from"
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()
  country_code1=Country.objects.filter(name_3char=country1)
  #Get app_name from session
  app_name = request.session['app_name'] if 'app_name' in request.session else ""
  '''Set query params with our changes'''
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  # Get Name in proper lang
  name = "name_%s" % lang
  # Setup the hash dictionary
  request_hash_dictionary1 = collections.OrderedDict()
  # Add prod class to request hash dictionary
  request_hash_dictionary['app_name'] = app_name
  request_hash_dictionary['lang'] = lang
  request_hash_dictionary['prod_class'] = prod_class

  #Set country_code to Country
  country_code1=Country.objects.get(name=country1)
  country_code2=Country.objects.get(name=country2)
  country_code_one=country_code1.name_3char.lower()
  country_code_two=country_code2.name_3char.lower()
  # Add the arguments to the request hash dictionary
  request_hash_dictionary['trade_flow'] = trade_flow
  request_hash_dictionary['country1'] = country_code_one
  request_hash_dictionary['country2'] = country_code_two
  request_hash_dictionary['product_dispaly'] = 'show'
  request_hash_dictionary['year'] = year

  # We are here, so let us store this data somewhere
  request_hash_string = "_".join(request_hash_dictionary.values())

  # Setup the store data
  store_data = request.build_absolute_uri().replace( "product_classification", "prod_class" ) + "||"
  store_page_url = request.build_absolute_uri().replace( "/api/", "/explore/" + app_name + "/" )
  store_page_url = store_page_url.replace( "data_type=json", "headless=true" )
  store_page_url = store_page_url.replace( "product_classification", "prod_class" )
  store_data = store_data + store_page_url + "||"
  store_data = store_data + request_hash_string

  # Write the store data to file
  store_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".store", "w+" )
  store_file.write( store_data )
  store_file.close()

  if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg" ) is True ):
    # Check the request data type
    if ( request.GET.get( 'data_type', None ) is None ):
      # Let us get the data from the file
      response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg", "r" )

      # Set the return data
      returnData = response_json_data.read()

      #"""Return to browser as JSON for AJAX request"""
      return HttpResponse( returnData )
    elif ( request.GET.get( 'data_type', '' ) == 'json' ):
      # Check if we have the valid json file
      if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ) is True ):
        # Let us get the data from the file
        response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "r" )

        # Set the return data
        returnData = response_json_data.read()

        #"""Return to browser as JSON for AJAX request"""
        return HttpResponse( returnData )
  '''Grab extraneous details'''
  if prod_class == "sitc4":
    # attr_list = list(Sitc4.objects.all().values('code','name','color'))
    attr_list = list(Sitc4.objects.all().values('code',name,'id','color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'color':i['color']}
     #.extra(where=['CHAR_LENGTH(code) = 2'])
  elif prod_class == "hs4":
    # attr_list = list(Hs4.objects.all().values('code','name')) #.extra(where=['CHAR_LENGTH(code) = 2'])
    attr_list = list(Hs4.objects.all().values('code',name,'id','community_id__color'))
    attr = {}
    for i in attr_list:
      attr[i['code']] = {'code':i['code'],'name':i[name],'item_id':i['id'],'color':i['community_id__color']}



  '''Define parameters for query'''
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "(export_value - import_value) as val"
  elif trade_flow == "net_import":
    val_col = "(import_value - export_value) as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
  else:
    val_col = "import_value as val"

  '''Create query'''
  q = """
    SELECT year, p.id, p.code, p.name_%s, p.community_id, c.name, c.color, %s, %s
    FROM %sobservatory_%s_ccpy as ccpy, %sobservatory_%s as p, %sobservatory_%s_community as c
    WHERE origin_id=%s and destination_id=%s and ccpy.product_id = p.id and p.community_id = c.id %s
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, DB_PREFIX, prod_class, DB_PREFIX, prod_class, DB_PREFIX, prod_class, country1.id, country2.id, year_where)

  """Prepare JSON response"""
  json_response = {}

  """Check cache"""
  if settings.REDIS:
    #raw = get_redis_connection('default')
    raw = redis.Redis("localhost")
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, country2.name_3char, "show", prod_class, trade_flow)
    # See if this key is already in the cache
    cache_query = raw.get(key)
    if(cache_query == None):
      rows = raw_q(query=q, params=None)
      total_val = sum([r[7] for r in rows])

      """Add percentage value to return vals"""
      # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[7], "rca":r[5],
               "share": (r[7] / total_val)*100,
               "community_id":r[4],"community_name":r[5],"color":r[6], "code":r[2], "id": r[2]} for r in rows]

      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

      json_response["data"] = rows

      # SAVE key in cache.
      raw.set(key, msgpack.dumps(rows))

    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded

  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[7] for r in rows])

    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[7], "rca":r[5],
             "share": (r[7] / total_val)*100,
             "community_id":r[4],"community_name":r[5],"color":r[6], "code":r[2], "id": r[2]} for r in rows]

    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

    json_response["data"] = rows

  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()

  magic = Cy.objects.filter(country=country1.id,
                            year__range=(years_available[0],
                                        years_available[-1])).values('year',
                                                                     'pc_constant',
                                                                     'pc_current',
                                                                     'notpc_constant')
  magic_numbers = {}
  for i in magic:
    magic_numbers[i['year']] = {"pc_constant":i['pc_constant'],
                                  "pc_current":i['pc_current'],
                                  "notpc_constant":i["notpc_constant"]}

  json_response["magic_numbers"] = magic_numbers
  json_response["attr_data"] = Sitc4.objects.get_all(lang) if prod_class == "sitc4" else Hs4.objects.get_all(lang)
  json_response["country1"] = country1.to_json()
  json_response["country2"] = country2.to_json()
  json_response["title"] = "What does %s %s %s %s?" % (country1.name, trade_flow, article, country2.name)
  json_response["year"] = year
  json_response["item_type"] = "product"
  json_response["app_type"] = "ccsy"
  json_response["prod_class"] =  prod_class
  json_response["attr"] = attr
  json_response["class"] =  prod_class
  json_response["other"] = query_params

  if not os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ):
    response_json_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "w+" )
    response_json_file.write( json.dumps( json_response ) )
    response_json_file.close()

  # raise Exception(time.time() - start)
  # Check the request data type
  if ( request.GET.get( 'data_type', None ) is None ):
    #"""Return to browser as JSON for AJAX request"""
    return HttpResponse( "" )
  elif ( request.GET.get( 'data_type', '' ) == 'json' ):
    """Return to browser as JSON for AJAX request"""
    return HttpResponse(json.dumps(json_response))

def api_cspy(request, trade_flow, country1, product, year):
  '''Init variables'''
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("prod_class", prod_class)
  lang = request.session['django_language'] if 'django_language' in request.session else "en"
  lang = request.GET.get("lang", lang)
  crawler = request.GET.get("_escaped_fragment_", False)
  country1 = Country.objects.get(name_3char=country1)
  #Get app_name from session
  app_name = request.session['app_name'] if 'app_name' in request.session else ""
  product = clean_product(product, prod_class)
  article = "to" if trade_flow == "export" else "from"

  '''Set query params with our changes'''
  query_params = request.GET.copy()
  query_params["lang"] = lang
  query_params["product_classification"] = prod_class
  # Setup the hash dictionary
  request_hash_dictionary = collections.OrderedDict()
  # Add prod class to request hash dictionary
  request_hash_dictionary['app_name'] = app_name
  request_hash_dictionary['lang'] = lang
  request_hash_dictionary['prod_class'] = prod_class
  #Set product code to particular product
  product_display = product.code
  # Add the arguments to the request hash dictionary
  request_hash_dictionary['trade_flow'] = trade_flow
  request_hash_dictionary['country1'] = country1
  request_hash_dictionary['country1'] = 'show'
  request_hash_dictionary['product_display'] = product_display
  request_hash_dictionary['year'] = year
  # We are here, so let us store this data somewhere
  request_hash_string = "_".join(request_hash_dictionary.values()) #base64.b64encode( request_unique_hash )

  # Setup the store data
  store_data = request.build_absolute_uri().replace( "product_classification", "prod_class" ) + "||"
  store_page_url = request.build_absolute_uri().replace( "/api/", "/explore/" + app_name + "/" )
  store_page_url = store_page_url.replace( "data_type=json", "headless=true" )
  store_page_url = store_page_url.replace( "product_classification", "prod_class" )
  store_data = store_data + store_page_url + "||"
  store_data = store_data + request_hash_string

  # Write the store data to file
  store_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".store", "w+" )
  store_file.write( store_data )
  store_file.close()

  if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg" ) is True ):
    # Check the request data type
    if ( request.GET.get( 'data_type', None ) is None ):
      # Let us get the data from the file
      response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".svg", "r" )

      # Set the return data
      returnData = response_json_data.read()

      #"""Return to browser as JSON for AJAX request"""
      return HttpResponse( returnData )
    elif ( request.GET.get( 'data_type', '' ) == 'json' ):
      # Check if we have the valid json file
      if ( os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ) is True ):
        # Let us get the data from the file
        response_json_data = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "r" )

        # Set the return data
        returnData = response_json_data.read()

        #"""Return to browser as JSON for AJAX request"""
        return HttpResponse( returnData )

  '''Grab extraneous details'''
  region_list = list(Country_region.objects.all().values()) #.extra(where=['CHAR_LENGTH(code) = 2'])
  region = {}
  for i in region_list:
    region[i['id']] = i

  continent_list = list(Country.objects.all().distinct().values('continent'))
  continents = {}
  for i,k in enumerate(continent_list):
     continents[k['continent']] = i*1000

  '''Define parameters for query'''
  year_where = "AND year = %s" % (year,) if crawler == "" else " "
  rca_col = "null"
  if trade_flow == "net_export":
    val_col = "(export_value - import_value) as val"
  elif trade_flow == "net_import":
    val_col = "(import_value - export_value) as val"
  elif trade_flow == "export":
    val_col = "export_value as val"
  else:
    val_col = "import_value as val"

  '''Create query'''
  q = """
    SELECT year, c.id, c.name_3char, c.name_%s, c.region_id, c.continent, %s, %s
    FROM %sobservatory_%s_ccpy as ccpy, %sobservatory_country as c
    WHERE origin_id=%s and ccpy.product_id=%s and ccpy.destination_id = c.id %s
    GROUP BY year, destination_id
    HAVING val > 0
    ORDER BY val DESC
    """ % (lang, val_col, rca_col, DB_PREFIX, prod_class, DB_PREFIX, country1.id, product.id, year_where)

  """Prepare JSON response"""
  json_response = {}

  """Check cache"""
  if settings.REDIS:
    raw = redis.Redis("localhost")
    key = "%s:%s:%s:%s:%s" % (country1.name_3char, "show", product.id,  prod_class, trade_flow)
    # See if this key is already in the cache
    cache_query = raw.get(key)

    if (cache_query == None):
      rows = raw_q(query=q, params=None)
      total_val = sum([r[6] for r in rows])

      """Add percentage value to return vals"""
      # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
      rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
               "region_id": r[4], "continent": r[5], "id":r[1]} for r in rows]

      if crawler == "":
        return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

      json_response["data"] = rows

      # SAVE key in cache.
      raw.set(key, msgpack.dumps(rows))

    else:
      # If already cached, now simply retrieve
      encoded = cache_query
      decoded = msgpack.loads(encoded)
      json_response["data"] = decoded

  else:
    rows = raw_q(query=q, params=None)
    total_val = sum([r[6] for r in rows])

    """Add percentage value to return vals"""
    # rows = [list(r) + [(r[4] / total_val)*100] for r in rows]
    rows = [{"year":r[0], "item_id":r[1], "abbrv":r[2], "name":r[3], "value":r[6], "rca":r[7], "share": (r[6] / total_val)*100,
             "region_id": r[4], "continent": r[5], "id":r[1]} for r in rows]

    if crawler == "":
      return [rows, total_val, ["#", "Year", "Abbrv", "Name", "Value", "RCA", "%"]]

    json_response["data"] = rows


  article = "to" if trade_flow == "export" else "from"

  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()

  magic = Cy.objects.filter(country=country1.id,
                            year__range=(years_available[0],
                                        years_available[-1])).values('year',
                                                                     'pc_constant',
                                                                     'pc_current',
                                                                     'notpc_constant')
  magic_numbers = {}
  for i in magic:
    magic_numbers[i['year']] = {"pc_constant":i['pc_constant'],
                                  "pc_current":i['pc_current'],
                                  "notpc_constant":i["notpc_constant"]}

  json_response["magic_numbers"] = magic_numbers
  json_response["attr_data"] = Country.objects.get_all(lang)
  json_response["title"] = "Where does %s %s %s %s?" % (country1.name, trade_flow, product.name_en, article)
  json_response["country1"] = country1.to_json()
  json_response["product"] = product.to_json()
  json_response["year"] = year
  json_response["item_type"] = "country"
  json_response["continents"]= continents
  json_response["region"]= region
  json_response["app_type"] = "cspy"
  json_response["class"] =  prod_class
  json_response["other"] = query_params

  if not os.path.exists( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json" ):
    response_json_file = open( settings.DATA_FILES_PATH + "/" + request_hash_string + ".json", "w+" )
    response_json_file.write( json.dumps( json_response ) )
    response_json_file.close()

  # raise Exception(time.time() - start)
  # Check the request data type
  if ( request.GET.get( 'data_type', None ) is None ):
    #"""Return to browser as JSON for AJAX request"""
    return HttpResponse( "" )
  elif ( request.GET.get( 'data_type', '' ) == 'json' ):
    """Return to browser as JSON for AJAX request"""
    return HttpResponse(json.dumps(json_response))

# Embed for iframe
def embed(request, app_name, trade_flow, country1, country2, product, year):
  lang = request.GET.get("lang", "en")
  prod_class = request.session['product_classification'] if 'product_classification' in request.session else "hs4"
  prod_class = request.GET.get("product_classification", prod_class)
  query_string = request.GET.copy()
  query_string["product_classification"] = prod_class
  # get distince years from db, different for diff product classifications
  years_available = list(Sitc4_cpy.objects.values_list("year", flat=True).distinct()) if prod_class == "sitc4" else list(Hs4_cpy.objects.values_list("year", flat=True).distinct())
  years_available.sort()

  return render_to_response("explore/embed.html", {"app":app_name, "trade_flow": trade_flow, "country1":country1, "country2":country2, "product":product, "year":year, "other":json.dumps(query_string),"years_available":json.dumps(years_available), "lang":lang})






###################
## Abandoned function? Coresponding model/tables 'wdi' & 'wdi_cwy'
###################
def get_similar_productive(country, year):
  # correlation = request.GET.get("c", "pearson")
  import math
  from scipy.stats.stats import pearsonr as cor_func
  # if correlation == "pearson":
  #   from scipy.stats.stats import pearsonr as cor_func
  # else:
  #   from scipy.stats.stats import spearmanr as cor_func
  y = year
  c = country
  country_lookup = get_country_lookup()
  prods = list(Sitc4.objects.filter(ps_size__isnull=False).values_list("id", flat=True))
  cpys = Sitc4_cpy.objects.filter(year=y, export_rca__isnull=False, export_rca__gt=0).values_list("country", "product", "export_rca")
  country_vectors = {}
  for cpy in cpys:
    if cpy[0] not in country_vectors:
      country_vectors[cpy[0]] = [0] * len(prods)
    try:
      prod_pos = prods.index(cpy[1])
      country_vectors[cpy[0]][prod_pos] = math.log(cpy[2]+0.1, 10)
    except:
      pass
  cors = []
  for this_c, rcas in country_vectors.items():
    # raise Exception(rcas, country_vectors[c.id])
    cors.append([country_lookup[this_c][0], country_lookup[this_c][1], cor_func(country_vectors[c.id], rcas)[0]])
    # raise Exception(cors)
  cors.sort(key=lambda x: x[2], reverse=True)
  return cors
  # raise Exception(cors)
  # raise Exception(cor_func(country_vectors[50], country_vectors[105]))
  return render_to_response("explore/similar.html", {"cors": cors})

###################
## Abandoned function? Coresponding model/tables 'wdi' & 'wdi_cwy'
###################
def similar_wdi(request, country, indicator, year):
  y = int(year)
  c = clean_country(country)
  if indicator == "0":
    this_index = 0
    name = "Productive strucuture correlation"
    values = get_similar_productive(c, y)
  else:
    i = Wdi.objects.get(pk=indicator)
    this_wdi = wdis = Wdi_cwy.objects.get(year=y, wdi=i, country=c)
    wdis = Wdi_cwy.objects.filter(year=y, wdi=i, country__region__isnull=False).order_by("-value")
    this_index = list(wdis).index(this_wdi)
    values = list(wdis.values_list("country__name_en", "country__name_3char", "value"))
    name = i.name
  return HttpResponse(json.dumps({"index": this_index, "values":values, "wdi": name}))



###############################################################################
## Helpers
###############################################################################
def clean_country(country):
  # first try looking up based on 3 character code
  try:
    c = Country.objects.get(name_3char=country)
  except Country.DoesNotExist:
    # next try 2 character code
    try:
      c = Country.objects.get(name_2char=country)
    except Country.DoesNotExist:
      c = None
  return c

def clean_product(product, prod_class):
  # first try looking up based on 3 character code
  if prod_class == "hs4":
    try:
      p = Hs4.objects.get(code=product)
    except Hs4.DoesNotExist:
      # next try SITC4
      try:
        conv_code = Sitc4.objects.get(code=product).conversion_code
        p = Hs4.objects.get(code=conv_code)
      except Hs4.DoesNotExist:
        p = None
  else:
    try:
      p = Sitc4.objects.get(code=product)
    except Sitc4.DoesNotExist:
      # next try SITC4
      try:
        conv_code = Hs4.objects.get(code=product).conversion_code
        p = Sitc4.objects.get(code=conv_code)
      except Hs4.DoesNotExist:
        p = None
  return p

def get_country_lookup():
  lookup = {}
  for c in Country.objects.all():
    lookup[c.id] = [c.name_en, c.name_3char]
  return lookup

def get_app_type(country1, country2, product, year):
  # country / all / show / year
  if country2 == "all" and product == "show":
    return "casy"

  # country / show / all / year
  elif country2 == "show" and product == "all":
    return "csay"

  # show / all / product / year
  elif country1 == "show" and country2 == "all":
    return "sapy"

  # country / country / show / year
  elif product == "show":
    return "ccsy"

  #  country / show / product / year
  else:
    return "cspy"
