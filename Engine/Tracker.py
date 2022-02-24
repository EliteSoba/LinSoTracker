import json
import os
from zipfile import ZipFile

import pygame

from Entities.EvolutionItem import EvolutionItem
from Entities.IncrementalItem import IncrementalItem
from Entities.Item import Item
from Tools.Bank import Bank
from Tools.CoreService import CoreService
from Tools.ImageSheet import ImageSheet


class Tracker:
    def __init__(self, template_name):
        self.kinds = None
        self.test_img = None
        self.items_sheet_data = None
        self.items_sheet = None
        self.tracker_json_data = None
        self.resources_path = None
        self.background_image = None
        self.items = pygame.sprite.Group()
        self.template_name = template_name
        self.core_service = CoreService()
        self.bank = Bank()
        self.extract_data()
        self.init_tracker()
        self.core_service.set_json_data(self.tracker_json_data)
        self.core_service.set_tracker_temp_path(self.resources_path)
        # pygame.display.set_mode((self.tracker_json_data[1]["Datas"]["Dimensions"]["width"], self.tracker_json_data[1]["Datas"]["Dimensions"]["height"]))
        print(self.tracker_json_data[1]["Datas"]["Background"])
        self.init_items()

    def extract_data(self):
        filename = os.path.join(self.core_service.get_app_path(), "templates", "{}.template".format(self.template_name))
        self.resources_path = os.path.join(self.core_service.get_temp_path(), "{}".format(self.template_name))
        self.core_service.create_directory(self.resources_path)
        print(self.resources_path)
        if os.path.isfile(filename):
            zip = ZipFile(filename)
            zip.extractall(self.resources_path)
            zip.close()

    def init_tracker(self):
        filename = os.path.join(self.resources_path, "tracker.json")
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                self.tracker_json_data = json.load(file)
                

        json_data_background = self.tracker_json_data[1]["Datas"]["Background"]
        self.background_image = self.bank.addImage(os.path.join(self.resources_path, json_data_background))

        json_data_item_sheet = self.tracker_json_data[1]["Datas"]["ItemSheet"]
        json_data_item_sheet_dimensions = self.tracker_json_data[1]["Datas"]["ItemSheetDimensions"]
        self.items_sheet = self.bank.addImage(os.path.join(self.resources_path, json_data_item_sheet))
        self.items_sheet_data = ImageSheet(self.items_sheet, json_data_item_sheet_dimensions["width"], json_data_item_sheet_dimensions["height"])

    def init_items(self):
        self.kinds = []
        for item in self.tracker_json_data[3]["Items"]:
            if item["Kind"] not in self.kinds:
                self.kinds.append(item["Kind"])

            if item["Kind"] == "EvolutionItem":
                item_image = self.items_sheet_data.getImageWithRowAndColumn(row=item["SheetPositions"]["row"],
                                                                            column=item["SheetPositions"]["column"])
                next_items_list = []
                for next_item in item["NextItems"]:
                    temp_item = {}
                    temp_item["Name"] = next_item["Name"]
                    temp_item["Image"] = self.items_sheet_data.getImageWithRowAndColumn(row=next_item["SheetPositions"]["row"], column=next_item["SheetPositions"]["column"])
                    temp_item["Label"] = next_item["Label"]
                    next_items_list.append(temp_item)
                print(temp_item)
                item = EvolutionItem(name=item["Name"],
                                     image=item_image,
                                     position=(item["Positions"]["x"], item["Positions"]["y"]),
                                     enable=item["isActive"],
                                     opacity_disable=item["OpacityDisable"],
                                     hint=item["Hint"],
                                     next_items=next_items_list,
                                     label=item["Label"],
                                     label_center=item["LabelCenter"])
                self.items.add(item)

            elif item["Kind"] == "IncrementalItem":
                print(item)
                item_image = self.items_sheet_data.getImageWithRowAndColumn(row=item["SheetPositions"]["row"],
                                                                            column=item["SheetPositions"]["column"])
                item = IncrementalItem(name=item["Name"],
                                       image=item_image,
                                       position=(item["Positions"]["x"], item["Positions"]["y"]),
                                       enable=item["isActive"],
                                       opacity_disable=item["OpacityDisable"],
                                       hint = item["Hint"],
                                       increments=item["Increment"])
                self.items.add(item)

            elif item["Kind"] == "Item":
                item_image = self.items_sheet_data.getImageWithRowAndColumn(row=item["SheetPositions"]["row"], column=item["SheetPositions"]["column"])
                item = Item(name=item["Name"],
                            image=item_image,
                            position=(item["Positions"]["x"], item["Positions"]["y"]),
                            enable=item["isActive"],
                            hint = item["Hint"],
                            opacity_disable=item["OpacityDisable"])
                self.items.add(item)

        print(self.kinds)

    def click(self, mouse_position, button):
        print(button)
        if button == 1:
            for item in self.items:
                if self.core_service.is_on_element(mouse_positions=mouse_position, element_positons=item.get_position(), element_dimension=(item.get_rect().w, item.get_rect().h)):
                    item.left_click()

        if button == 3:
            for item in self.items:
                if self.core_service.is_on_element(mouse_positions=mouse_position, element_positons=item.get_position(), element_dimension=(item.get_rect().w, item.get_rect().h)):
                    item.right_click()


    def draw(self, screen):
        # pass
        screen.blit(self.background_image, (0, 0))
        self.items.draw(screen)
        # self.items.update()
        # screen.blit(self.items_sheet, (50, 50))