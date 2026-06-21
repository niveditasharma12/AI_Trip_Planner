import os
from utils.place_info_search import TavilyPlaceSearchTool
from typing import List
from langchain.tools import tool
from dotenv import load_dotenv

class PlaceSearchTool:
    def __init__(self):
        load_dotenv()
        self.tavily_search = TavilyPlaceSearchTool()
        self.place_search_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools using Tavily search with clean string outputs"""
        
        @tool
        def search_attractions(place: str) -> str:
            """Search attractions of a place"""
            try:
                # Force the output to be a plain clean string
                tavily_result = str(self.tavily_search.tavily_search_attractions(place))
                return f"Following are the attractions of {place}: {tavily_result}"
            except Exception as e:
                return f"Error gathering attractions for {place}: {str(e)}"
        
        @tool
        def search_restaurants(place: str) -> str:
            """Search restaurants of a place"""
            try:
                tavily_result = str(self.tavily_search.tavily_search_restaurants(place))
                return f"Following are the recommended restaurants of {place}: {tavily_result}"
            except Exception as e:
                return f"Error gathering restaurants for {place}: {str(e)}"
        
        @tool
        def search_activities(place: str) -> str:
            """Search activities of a place"""
            try:
                tavily_result = str(self.tavily_search.tavily_search_activity(place))
                return f"Following are the activities in and around {place}: {tavily_result}"
            except Exception as e:
                return f"Error gathering activities for {place}: {str(e)}"
        
        @tool
        def search_transportation(place: str) -> str:
            """Search transportation of a place"""
            try:
                tavily_result = str(self.tavily_search.tavily_search_transportation(place))
                return f"Following are the modes of transportation available in {place}: {tavily_result}"
            except Exception as e:
                return f"Error gathering transportation info for {place}: {str(e)}"
        
        return [search_attractions, search_restaurants, search_activities, search_transportation]