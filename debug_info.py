

def get_info():
    main = __import__('__main__').__dict__.get('_main_launcher_object')
    if not main:
        return []

    def iter_menu(root, indent=0):
        lines = []
        for elem in root.actions:
            if elem.type == 'item':
                lines.append('{}{}'.format(' ' * indent, elem.text))
            elif elem.type == 'menu':
                lines.append('{}<b>{}</b> <i>[name: {}]</i>'.format(' ' * indent, elem.text, elem.name or '-'))
                lines.extend(iter_menu(elem, indent + 2))
        return lines

    lines = iter_menu(main.tray_menu.root_menu)
    return [dict(
        title='Menu',
        html='\n'.join(lines)
    )]
