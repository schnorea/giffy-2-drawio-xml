#!/usr/bin/env python3

import json
import string
import random
import argparse

from bs4 import BeautifulSoup

draw_obj_keys = {'x': 1, 'y': 1, 
    'rotation': 1, 'id': 1, 
    'width': 1, 'height': 1, 
    'uid': 1, 'order': 1, 
    'lockAspectRatio': 1, 'lockShape': 1, 
    'constraints': 1, 'graphic': 1, 
    'linkMap': 1, 'hidden': 1, 
    'layerId': 1, 'flipHorizontal': 1, 
    'flipVertical': 1, 'children': 1}

# From stackoverflow with mods
def id_generator(size=20, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

class Gliffy(object):
    def __init__(self, filename):
        self.draw_objs = []
        self.obj_keys = {}
        self.draw_io_id = id_generator()
        with open(filename, "r") as ifh:
            self.gobj = json.load(ifh)
            self.stage = self.gobj['stage']
            self.raw_draw_objs = self.stage['objects']
            # print(self.raw_draw_objs)
            for raw_draw_obj in self.raw_draw_objs:
                dobj = GliffyObj(raw_draw_obj)
                #print(dobj)
                self.draw_objs.append(dobj)


    def emit_drawio(self):
        text_array = []
        text_array.append('<?xml version="1.0" encoding="UTF-8"?>')
        text_array.append('<mxfile host="Electron" modified="2021-06-09T19:48:40.870Z" agent="5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) draw.io/14.5.1 Chrome/89.0.4389.82 Electron/12.0.1 Safari/537.36" etag="43a6SbNFbkbtn3BeCMYf" version="14.5.1" type="device">')
        text_array.append('<diagram id="Q0eEivNgb1EWn1eKrHUD" name="Page-1">')
        text_array.append('<mxGraphModel dx="1426" dy="1025" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">')
        text_array.append('<root>')
        text_array.append('<mxCell id="0" />')
        text_array.append('<mxCell id="1" parent="0" />')
        placement = []
        for i, draw_obj in enumerate(self.draw_objs):
            #print(i)
            #print(draw_obj.emit_drawio(i+1))
            text_array.extend(draw_obj.emit_drawio_shapes(i+1))
            if draw_obj.placement is not None:
                placement.append(draw_obj.placement)
    
        #print(placement)
        text_array.append('</root>')
        text_array.append('</mxGraphModel>')
        text_array.append('</diagram>')
        text_array.append('</mxfile>')

        return '\n'.join(text_array)

        if False:
            keys = list(raw_draw_objs.keys())

            if False:
                for key in keys:
                    print()
                    print()
                    print("Key", key)
                    print(raw_draw_objs[key])
                    print()

            stage = raw_draw_objs['stage']

            vobj = stage
            keys = list(vobj.keys())
            if False:
                for key in keys:
                    print()
                    print()
                    print("Key", key)
                    print(vobj[key])
                    print()

            vobj = stage['objects'][67]
            keys = list(vobj.keys())
            if False:
                for key in keys:
                    print()
                    print()
                    print("Key", key)
                    print(vobj[key])

            if True:
                for key in keys:
                    print(f"        self.{key} = self.obj.get('{key}', None)")


class GliffyObj(object):
    def __init__(self, raw_draw_obj):
        self.obj = raw_draw_obj
        self.my_children = []
        self._populate()

    def _populate(self):
        self.x = self.obj.get('x', None)
        self.y = self.obj.get('y', None)
        self.rotation = self.obj.get('rotation', None)
        self.id = self.obj.get('id', None)
        self.width = self.obj.get('width', None)
        self.height = self.obj.get('height', None)
        self.uid = self.obj.get('uid', None)
        self.order = self.obj.get('order', None)
        self.lockAspectRatio = self.obj.get('lockAspectRatio', None)
        self.lockShape = self.obj.get('lockShape', None)
        self.constraints = self.obj.get('constraints', None)
        self.graphic = self.obj.get('graphic', None)
        self.linkMap = self.obj.get('linkMap', None)
        self.children = self.obj.get('children', None)
        self.hidden = self.obj.get('hidden', None)
        self.layerId = self.obj.get('layerId', None)
        self.flipHorizontal = self.obj.get('flipHorizontal', None)
        self.flipVertical = self.obj.get('flipVertical', None)
        self.text = None
        self._get_graphic()
        # Check for new fields

    def _shape_drawio(self,tid):
        self.shape_lookup_drawio = {
            "com.gliffy.stencil.ellipse.basic_v1": "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#ffe6cc;strokeColor=#d79b00;",
            "com.gliffy.stencil.rhombus.basic_v1": "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;",
            "com.gliffy.stencil.start_end.flowchart_v1": "strokeWidth=1;html=1;shape=mxgraph.flowchart.start_2;whiteSpace=wrap;",
            "com.gliffy.stencil.diamond.basic_v1": "strokeWidth=1;html=1;shape=mxgraph.flowchart.decision;whiteSpace=wrap;",
            "com.gliffy.stencil.document.flowchart_v1": "shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;darkOpacity=0.05;size=8;",
            "com.gliffy.stencil.rectangle.basic_v1": "rounded=0;whiteSpace=wrap;html=1;",
            "com.gliffy.stencil.network.network_v4.business.user": "shape=actor;whiteSpace=wrap;html=1;labelPosition=center;verticalLabelPosition=bottom;align=center;verticalAlign=top;"
        }
        drawio_shape = self.shape_lookup_drawio.get(tid, None)
        if drawio_shape is None:
            print(f"WARNING: Giffy tid {tid} doesn't have a translation. Giving it an ORANGE RECTANGLE for now")
            print(f"         Adjust data structure self.shape_lookup_drawio to add new translation.\n")
            return "rounded=0;whiteSpace=wrap;html=1;fillColor=#FF8000;"
        
        return drawio_shape

    def _get_text(self):
        text = ""

        if self.text is not None:
            soup = BeautifulSoup(self.text, 'lxml')
            text = soup.text
            text = text.replace('&', '&amp;')
            text = text.replace('"', '&quot;')

        return text

    def emit_drawio_shapes(self, number):
        output = []
        self.placement = None
        if self.type == 'Shape':
            # <mxCell id="WpHb4AEowC1BbJerPiXC-2" value="Text for the&amp;nbsp;&lt;br&gt;ages" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
            #   <mxGeometry x="200" y="420" width="120" height="60" as="geometry" />
            # </mxCell>
            text = ""
            if len(self.my_children) > 0:
                for child in self.my_children:
                    child._get_text()
                    text = text + child._get_text()

            style = self._shape_drawio(self.tid)
            x = self.x
            y = self.y
            width = self.width
            height = self.height

            self.placement = {f"{self.draw_io_id}-{number}": [x,y,width,height]}

            mxCell_open = f'<mxCell id="{self.draw_io_id}-{number}" value="{text}" style="{style}" vertex="1" parent="1">'
            mxGeometry = f'\t<mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry" />'
            mxCell_close = '</mxCell>'
            output = [mxCell_open, mxGeometry, mxCell_close]
        return output

    def emit_drawio_lines(self, number):
        """Not Complete or even Called"""
        output = []
        self.placement = None
        if self.type == 'Line':
            # <mxCell id="WpHb4AEowC1BbJerPiXC-5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="WpHb4AEowC1BbJerPiXC-3" target="WpHb4AEowC1BbJerPiXC-2">
            # <mxGeometry relative="1" as="geometry" />
            # </mxCell>
            text = ""
            if len(self.my_children) > 0:
                for child in self.my_children:
                    child._get_text()
                    text = text + child._get_text()

            style = self._shape_drawio(self.tid)
            x = self.x
            y = self.y
            width = self.width
            height = self.height

            self.placement = {f"{self.draw_io_id}-{number}": [x,y,width,height]}

            mxCell_open = f'<mxCell id="{self.draw_io_id}-{number}" value="{text}" style="{style}" vertex="1" parent="1">'
            mxGeometry = f'\t<mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" as="geometry" />'
            mxCell_close = '</mxCell>'
            output = [mxCell_open, mxGeometry, mxCell_close]
        return output


    def _get_graphic(self):
        #print(self.graphic)
        #print()

        self.type = self.graphic.get('type', None)

        #print(self.type)

        if self.type == 'Shape':
            self.shape = self.graphic['Shape']
            self.tid = self.shape['tid']
            #print(list(self.shape.keys()))
            #print(self.tid)
            if self.children is not None:
                #print(self.children)
                for child in self.children:
                    self.my_children.append(GliffyObj(child))
            #print()
            
        elif self.type == 'Line':
            self.line = self.graphic['Line']
            print(self.line)
            print()

            #print(list(line.keys()))

        elif self.type == 'Text':
            self.text = self.graphic['Text']['html']

        else: 
            print("WARNING: FOUND SOMETHING UNEXPECTED")

    def give_me_keys(self):
        key_list = list(self.obj.keys())
        # {key: value for (key, value) in iterable}
        key_dict = {key: 1 for key in key_list}
        return(key_dict)


if __name__ == "__main__":
        # Parse the CLI
    parser = argparse.ArgumentParser(description='Convert (partially) Gliffy drawings to Draw.io/Diagram.net drawings ')
    parser.add_argument('gliffy_drawing',
                        help='Name of the gliffy to convert')
    parser.add_argument('drawio_drawing_xml',
                        help='Name of the output drawio aware xml document. Example: "ThanksGliffy.xml"')
    args = parser.parse_args()

    print("Attempting to convert:")
    print("\tGliffy File", args.gliffy_drawing)
    print("\tDraw.io XML File", args.drawio_drawing_xml)

    glif = Gliffy(args.gliffy_drawing)

    with open(args.drawio_drawing_xml, "w") as ofh:
        ofh.write(glif.emit_drawio())
