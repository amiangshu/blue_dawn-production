from django.shortcuts import render, redirect
from templates.JSONDataSet import JSONDataSet
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.files import File
from django.http import HttpResponse
from django.utils.encoding import smart_str
import os

# display json data on a table
@login_required(login_url="/login")
def viewdata(request):
    parameter = request.GET.get('dataset', '')
    if (parameter != ""):
        id = parameter.split('-', 1)[1]
        dataset = JSONDataSet.GetDataset(id)
    else:
        return render(request,'index.html')

    context = {
        'data': dataset.GetResponseMatrix(False),
        'questions': dataset.GetQuestions(False),
        'tags': dataset.GetTags(),
        'id': id,
    }
    return render(request, 'viewdata.html', context=context)

def addtag(request):
    toreturn = dict()
    try:
        dataset = JSONDataSet.GetDataset(request.POST.get("id"))

        if (dataset.HasTag(request.POST.get("tag"))):
            toreturn['results'] = False
            toreturn['message'] = "Tag already exists"
        else:
            if (request.POST.get('tag') == ""):
                toreturn['results'] = False
                toreturn['message'] = "Tag cannot be empty"
            else:
                dataset.AddTag(request.POST.get('tag'))
                dataset.SaveDataset(request.user)
                toreturn['results']=True

    except Exception as e:
        toreturn['results']=False
        toreturn['message']=str(e)
    return JsonResponse(toreturn)

def TagItem(request):
    toreturn = dict()
    try:
        dataset = JSONDataSet.GetDataset(request.POST.get("datasetId"))
        if (dataset.ItemHasTag(request.POST.get("rid"), request.POST.getlist('tags[]')[-1])):
            toreturn['result'] = False
            toreturn['message'] = "Item already has that tag"
        else:
            dataset.TagItem(request.POST.get("rid"), request.POST.getlist("tags[]"))
            dataset.SaveDataset(request.user)
            toreturn["result"] = True
    except Exception as e:
        toreturn['result'] = False
        toreturn['message'] = str(e)
    return JsonResponse(toreturn);

def removetag(request):
    toreturn = dict()
    try:
        dataset = JSONDataSet.GetDataset(request.POST.get("id"))
        dataset.RemoveTag(request.POST.get("tag"))
        dataset.SaveDataset(request.user)
        toreturn["results"] = True
    except Exception as e:
        toreturn['results'] = False
        toreturn['message'] = str(e)

    return JsonResponse(toreturn)

def RemoveItemTag(request):
    toreturn = dict()
    try:
        dataset = JSONDataSet.GetDataset(request.POST.get("id"))
        dataset.RemoveItemTag(request.POST.get("rid"), request.POST.get("tag"))
        dataset.SaveDataset(request.user)
        toreturn['results'] = True
    except Exception as e:
        toreturn['results'] = False
        toreturn['message'] = str(e)

    return JsonResponse(toreturn)


def ExportCSV(request):
    dataset = JSONDataSet.GetDataset(request.GET.get('id'))
    dataset.ExportCSV(request.user)

    file_name = dataset.json_dict['title'] + ".csv"
    fpntr = File(open("media/tmp/" + file_name))

    response = HttpResponse(fpntr, content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)

    os.remove("media/tmp/" + file_name)

    return response

def ExportXLSX(request):
    dataset = JSONDataSet.GetDataset(request.GET.get('id'))
    dataset.ExportXLSX(request.user)

    file_name = dataset.json_dict['title'] + ".xlsx"
    fpntr = File(open("media/tmp/" + file_name, 'rb'))

    response = HttpResponse(fpntr, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_name)

    os.remove("media/tmp/" + file_name)

    return response

#deleting the whole dataset from the viewdata page
def DeleteDataSet(request):
    #get the dataset by "id" by passing the dataset's id to the "GetDataset" method in the JSONDataSet.py file
    dataset = JSONDataSet.GetDataset(request.GET.get('id'))
    #after getting the desired dataset, it passed to DeleteDataSet method in the the JSONDataSet.py file
    dataset.DeleteDataSet(request.user)
    username = request.user.username

    return redirect('http://127.0.0.1:8000/userpage/')
