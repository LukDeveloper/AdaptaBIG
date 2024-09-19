import xml.etree.ElementTree as ET
import urllib.request, json
import os

url_base = 'https://sistema.adaptabrasil.mcti.gov.br'

recorte = 'brasil'

resolucao = 'municipio'

schema = 'adaptabrasil'

# Definindo namespaces
namespaces = {
    'gmd': 'http://www.isotc211.org/2005/gmd',
    'gco': 'http://www.isotc211.org/2005/gco'
}

# Register namespaces
for prefix, uri in namespaces.items():
    ET.register_namespace(prefix, uri)

def getScenarios(dict_scenarios: dict)->str:
    scenarios = ''
    for scenario in dict_scenarios:
        scenarios += f"{scenario['label']} "
    return scenarios

def update_xml_indicator_with_data(xml_template, indicador: list, years: list):
    tree = ET.ElementTree(ET.fromstring(xml_template))
    root = tree.getroot()

    # Adicionando valor para o "Título"
    title = root.find('.//gmd:title/gco:CharacterString', namespaces)
    if title is not None:
        title.text = indicador.get('title', '')

    # Adicionando valor para "Resumo"
    abstract = root.find('.//gmd:abstract/gco:CharacterString', namespaces)
    if abstract is not None:
        abstract.text = indicador.get('simple_description', '')

    url_show_map_on_the_site = f"{url_base}/{indicador['id']}/1/{years[0]}/null/{recorte}/" \
                               f"{resolucao}/{schema}"

    # Adicionando valor para "Overview (URL da imagem)"
    overview = root.find('.//gmd:MD_BrowseGraphic/gmd:fileName/gco:CharacterString', namespaces)
    if overview is not None:
        overview.text = indicador.get(url_show_map_on_the_site, '')

    # Adicionando valor para "Palavras-chave"
    keywords = root.findall('.//gmd:keyword/gco:CharacterString', namespaces)
    for i, keyword in enumerate(keywords):
        key = f'keyword_{i+1}'
        keyword.text = indicador.get(key, '')

    # Adicionando valor para "Recursos Online" e "Descrição do resurso online"
    online_resources = root.findall('.//gmd:CI_OnlineResource/gmd:linkage/gmd:URL', namespaces)
    online_resources_desc = root.findall('.//gmd:CI_OnlineResource/gmd:description/gco:CharacterString', namespaces)
    for i, resource in enumerate(online_resources):
        key = f'online_resource_url_{i+1}'
        resource.text = indicador.get(key, '')
    for i, resource in enumerate(online_resources_desc):
        key = f'online_resource_url_desc_{i+1}'
        resource.text = indicador.get(key, '')
    return tree


# Dados AdaptaBrasil

url_hierarchy = 'https://sistema.adaptabrasil.mcti.gov.br/api/hierarquia/adaptabrasil'

if __name__ == '__main__':
    url = urllib.request.urlopen(url_hierarchy)
    indicadores = json.load(url)

    # Caminho para Template XML ISO19115/19139
    with open('input.xml', 'r', encoding='utf-8') as file:
        xml_template = file.read()

    # Diretório para salvar os arquivos XML de saída
    output_dir = 'output_xml_files'
    os.makedirs(output_dir, exist_ok=True)

    # Gera arquivos XML para cada registro
    # for i, record in enumerate(exemplo_dados, start=1):
    #     tree = update_xml_with_data(xml_template, record)
    #     output_file = os.path.join(output_dir, f'record_{i}.xml')
    #     tree.write(output_file, encoding='UTF-8', xml_declaration=True)
    for i, indicador in enumerate(indicadores):
        if indicador['level'] < 2:
            continue
        years = None
        if indicador['years'] is None:
            pass
        elif type(indicador['years']) is list:
            years = indicador['years']
        else:
            years = indicador['years'].split(',')
        tree = update_xml_indicator_with_data(xml_template, indicador ,years)
        output_file = os.path.join(output_dir, f'record_{i}.xml')
        tree.write(output_file, encoding='UTF-8', xml_declaration=True)
        if i > 20:
            break
    print(f'{len(exemplo_dados)} arquivos XML foram gerados em {output_dir}')