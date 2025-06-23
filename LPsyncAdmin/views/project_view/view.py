from django.shortcuts import render, redirect
from django.urls import reverse
from LPsyncAdmin.models import Project, Sitemap, User
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def view(request, pk):
    if 'email' in request.session:
        current_user = User.objects.get(email=request.session['email'])
        if current_user.pk != pk:
            return redirect('401_forbidden')
        # Filter projects to show only those belonging to the current user
        project = Project.objects.filter(user=current_user)
        return render(request, "project/project-view.html", {'project': project, 'user': current_user})
    else:
        return redirect('login')

def scrape_sitemaps(request, project_id):
    try:
        project = Project.objects.get(id=project_id)

        # Additional security check: ensure the project belongs to the current user
        if 'email' in request.session:
            current_user_email = request.session['email']
            current_user = User.objects.get(email=current_user_email)
            if project.user != current_user:
                return redirect('401_forbidden')
        else:
            return redirect('login')
        
        base_url = project.product_website
        if not base_url.startswith(('http://', 'https://')):
            base_url = 'https://' + base_url
        
        collection_prefix = urljoin(base_url, "collections")
        
        response = requests.get(base_url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.content, "html.parser")
        
        sitemap_links = set()
        
        for nav_element in soup.find_all('ul', class_='list-unstyled', attrs={'role': 'list'}):
            for a_tag in nav_element.find_all('a', href=True):
                link = urljoin(base_url, a_tag['href'])
                # Filter for collection links or any relevant links you want to consider as sitemaps
                if link.startswith(collection_prefix):
                    link_text = a_tag.get_text().strip()
                    category = link_text if link_text else "Uncategorized"
                    
                    # Create a sitemap entry for each link
                    Sitemap.objects.update_or_create(
                        url=link,
                        sitemap_name=link_text or f"Sitemap {len(sitemap_links) + 1}",
                        category=category,
                        project_id=project_id,
                        user=project.user
                    )
                    sitemap_links.add(link)
        
        # If no links were found using collection_prefix, try a broader approach
        if not sitemap_links:
            # Look for all links
            for a_tag in soup.find_all('a', href=True):
                link = urljoin(base_url, a_tag['href'])
                # Skip external links and anchor links
                if link.startswith(base_url) and '#' not in link:
                    link_text = a_tag.get_text().strip()
                    category = "Main Navigation"
                    
                    # Create a sitemap entry
                    Sitemap.objects.update_or_create(
                        url=link,
                        sitemap_name=link_text or f"Sitemap {len(sitemap_links) + 1}",
                        category=category,
                        project_id=project_id,
                        user=project.user
                    )
                    sitemap_links.add(link)
        
        if sitemap_links:
            # return redirect(reverse('site_map', kwargs={'pk': project.user.pk}))
            return redirect('s_cards')
        else:
            return redirect('401_forbidden')
            
    except Project.DoesNotExist:
        return redirect('401_forbidden')
    except requests.RequestException as e:
        return redirect('401_forbidden')
    except Exception as e:
        return redirect('401_forbidden')