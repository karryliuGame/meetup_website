from django.shortcuts import render, redirect
import calendar
from calendar import HTMLCalendar
from datetime import datetime
from .models import Event, Venue
from .forms import VenueForm, EventForm
from django.http import HttpResponsePermanentRedirect
from django.http import HttpResponse
import csv

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# Import Pagination Stuff
from django.core.paginator import Paginator

def venue_pdf(request):
    # Create Bytestream buffer
    buf = io.BytesIO()
    # Create a canvas 
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    # create a text object
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica",14)
    
    # lines = ["This is line 1",
    #          "This is line 2",
    #          "This is line 3",
    #          ]
    # Designate The Model
    venues = Venue.objects.all()

    lines = []
    for venue in venues:
        lines.append(venue.name)
        lines.append(venue.address)
        lines.append(venue.zip_code)
        lines.append(venue.phone)
        lines.append(venue.web)
        lines.append(venue.email_address)
        lines.append("  ")
        
    for line in lines:
        textob.textLine(line)
        
    c.drawText(textob)
    c.showPage()
    c.save()
    buf.seek(0)
    
    return FileResponse(buf, as_attachment=True, filename="venue.pdf")
    
def venue_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=venues.csv'
    
    # Crete a csv writer
    writer = csv.writer(response)
    
    # Designate The Model
    venues = Venue.objects.all()
    
    # Add column headings to the csv file
    writer.writerow(['Venue Name', 'Address', 'Zip Code', 'Phone', 'Web Address', 'Email Address'])
    for venue in venues:
        writer.writerow([venue.name, venue.address, venue.zip_code, venue.web, venue.email_address])
    
    return response


def venue_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=venues.txt'
    # Designate The Model
    venues = Venue.objects.all()
    lines = []
    for venue in venues:
        lines.append(f'{venue.name}\n{venue.address}\n{venue.zip_code}\n{venue.web}\n{venue.email_address}\n\n\n')
    
    response.writelines(lines)
    return response

#Delete an Event
def delete_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    event.delete()
    return redirect('list-events')

#Delete an Venue
def delete_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    venue.delete()
    return redirect('list-venues')

def update_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        return redirect('list-events')
        
    return render(request, 'myclub/update_event.html', {
        'event': event, 'form': form,
        })

def add_event(request):
    submitted = False
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponsePermanentRedirect('/add_event?submitted=True')
    else:
        form = EventForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'myclub/add_event.html', {'form':form, 'submitted': submitted})

def update_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    form = VenueForm(request.POST or None, instance=venue)
    if form.is_valid():
        form.save()
        return redirect('list-venues')
        
    return render(request, 'myclub/update_venue.html', {
        'venue': venue, 'form': form,
        })

def search_venues(request):
    if request.method == "POST":
        searched = request.POST['searched']
        venues = Venue.objects.filter(name__contains =searched)
        return render(request, 'myclub/search_venues.html', {'searched':searched,'venues':venues})
    else:
        return render(request, 'myclub/search_venues.html', {})


def show_venue(request, venue_id):
    venue = Venue.objects.get(pk=venue_id)
    return render(request, 'myclub/show_venue.html', {
        'venue': venue,
        })


def list_venues(request):
    #venue_list = Venue.objects.all().order_by('name')
    #venue_list = Venue.objects.all().order_by('?') # order randomly
    venue_list = Venue.objects.all()
    
    # set up pagination
    p = Paginator(Venue.objects.all(),2)
    page = request.GET.get('page')
    venues = p.get_page(page)
    
    return render(request, 'myclub/venues.html', {
        'venue_list': venue_list,
        'venues': venues
        })

def add_venue(request):
    submitted = False
    if request.method == "POST":
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponsePermanentRedirect('/add_venue?submitted=True')
    else:
        form = VenueForm
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'myclub/add_venue.html', {'form':form, 'submitted': submitted})


def all_events(request):
    #event_list = Event.objects.all().order_by('name','venue')
    event_list = Event.objects.all().order_by('-event_date')
    return render(request, 'myclub/event_list.html', {
        'event_list': event_list,
        })

def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    name = "John"
    month = month.capitalize()
    
    #Covert month from name to number
    month_number = int(list(calendar.month_name).index(month))
    
    # create a calender
    cal = HTMLCalendar().formatmonth(
        year, 
        month_number)
    
    now = datetime.now()
    current_year = now.year 

    # get current time
    time = now.strftime('%I:%M %p')
    return render(request, 'myclub/home.html', {
        "name": name,
        "year": year,
        "month": month,
        "month_number": month_number,
        "cal": cal,
        "current_year": current_year,
        "time": time,
        })

def about(request):
    return render(request, 'myclub/about.html', {})

