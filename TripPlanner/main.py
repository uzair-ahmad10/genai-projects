from crewai import Process, Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from dotenv import load_dotenv
load_dotenv()

# =======================================================================================================
# TOOLS FOR AGENT 
# =======================================================================================================

web_search_tool = SerperDevTool()
scrapper_tool = ScrapeWebsiteTool()


# =======================================================================================================
# LLM MODEL DEFINITION 
# =======================================================================================================
llm = LLM(model='openrouter/nvidia/nemotron-3-ultra-550b-a55b:free', stream = True)


# =========================================================================================================
# AGENTS DEFINITION
# =========================================================================================================

activity_planner = Agent(
    role = "Personalized Activity Planner",
    goal="Analyze user preferences and suggest an exciting surprise destination along with a curated list of themed activities.",
    backstory="You are a master of surprises and a world-renowned travel planner. You excel at reading between the lines of traveler preferences to uncover the perfect secret destination and unique experiences they wouldn't find on their own.",
    verbose = True,
    tools = [web_search_tool,scrapper_tool],
    allow_delegation=False,
    llm = llm
)

restaurant_scout =Agent(
    role= "Restaurant and Scenic Location Scout",
    goal = "Discover top-rated, hidden gem restaurants and breathtaking scenic spots at the chosen destination.",
    backstory="You are an elite food critic and location scout. You know how to find places that offer not just a meal, but an unforgettable experience with stunning views.",
    tools = [web_search_tool,scrapper_tool],
    verbose = True,
    allow_delegation = False,
    llm = llm
)

itinerary_compiler = Agent(
    role="Itinerary Compiler",
    goal="Compile all research into a cohesive, perfectly timed surprise travel itinerary.",
    backstory="You are a meticulous logistician and master storyteller. You take raw ideas, locations, and restaurants, and weave them into a flawless, daily itinerary that maximizes joy and minimizes travel friction.",
    # This agent doesn't need search tools; its job is to format the data found by the others
    tools=[],
    verbose=True,
    allow_delegation=False,
    llm = llm
)

# ========================================================================================================
# TASKS
# ========================================================================================================

activity_planning_task = Task(

    description="Analyze the traveler's origin ({origin}), travel dates ({travel_dates}), and interests ({interests}). Suggest 3 potential surprise destinations. Choose the best one and list 5 unique activities tailored to their interests.",
    expected_output="A final selected destination and a detailed list of 5 personalized activities.",
    agent=activity_planner
)

# Task 2: Restaurant Scouting (Assigned to restaurant_scout)
restaurant_scout_task = Task(
    description="Based on the final destination chosen by the Activity Planner, find 3 incredible restaurants and 2 scenic spots. Focus on places that match the traveler's core interests: {interests}.",
    expected_output="A curated list of 3 restaurants and 2 scenic locations, including brief descriptions and reasons for selection.",
    agent=restaurant_scout
)

# Task 3: Itinerary Compilation (Assigned to itinerary_compiler)
itinerary_compilation_task = Task(
    description="Take the destination, activities, restaurants, and scenic spots from the previous tasks. Create a detailed, day-by-day itinerary for {travel_dates}. Include travel logistics originating from {origin}.",
    expected_output="A beautifully formatted, detailed daily itinerary document in Markdown format.",
    agent=itinerary_compiler
)


surprise_trip_crew = Crew(
    agents=[activity_planner, restaurant_scout, itinerary_compiler],
    tasks=[activity_planning_task, restaurant_scout_task, itinerary_compilation_task],
    process=Process.sequential,
    verbose=True
)

# =======================================================================================================
# EXECUTION SCRIPT
# =======================================================================================================

if __name__ == '__main__':

    origin = input(str("Enter the Travel location: "))
    
    if(origin):
        print("Thanks for Sharing with us...")
    
    travel_dates = input(str("Enter the travel dates: "))

    if(travel_dates):
        print("Thanks for Sharing with us...")
    
    interests = input(str("Tell us about things that you like the most: "))

    if(interests):
        print("Thanks for sharing with us...")

    input_query = {
        'origin': origin,
        'travel_dates': travel_dates,
        'interests': interests
    }

    result = surprise_trip_crew.kickoff(inputs=input_query)

    print("##################################################")
    print("🎉 SURPRISE TRIP ITINERARY GENERATED 🎉")
    print("##################################################\n")

    print(result.raw)
