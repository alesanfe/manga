# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present Manga Project
"""
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

# Import centralized logger configuration
from utils.logger_config import logger


@login_required(login_url="/login/")
def index(request):
    return redirect('list_all_mangas')


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        logger.debug(f"Loading page: {request.path}")
        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        logger.debug(f"Loading template: {load_template}")
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        logger.error(f"Error loading page: {e}")
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
