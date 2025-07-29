import streamlit as st
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import altair as alt
from PIL import Image
import base64

# Set page configuration
st.set_page_config(
    page_title="Pet Selection Advisor",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS to style the application
def local_css():
    st.markdown("""
    <style>
        /* Main color scheme */
        :root {
            --primary-color: #4e89ae;
            --secondary-color: #43658b;
            --accent-color: #ed6663;
            --background-color: #f9f9f9;
            --text-color: #333333;
            --light-gray: #e0e0e0;
        }

        /* General styling */
        .main {
            background-color: var(--background-color);
            color: var(--text-color);
            font-family: 'Roboto', sans-serif;
        }

        h1, h2, h3 {
            color: var(--primary-color);
            font-weight: 600;
        }

        /* Header styling */
        .header-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 0;
            border-bottom: 2px solid var(--light-gray);
            margin-bottom: 2rem;
        }

        .app-header {
            color: var(--primary-color);
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
        }

        /* Card styling for pet recommendations */
        .pet-card {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: transform 0.3s ease;
        }

        .pet-card:hover {
            transform: translateY(-5px);
        }

        .pet-card h3 {
            color: var(--primary-color);
            margin-top: 0;
            border-bottom: 1px solid var(--light-gray);
            padding-bottom: 0.5rem;
        }

        .pet-card-content {
            display: flex;
            flex-direction: row;
        }

        .pet-card-image {
            width: 150px;
            height: 150px;
            object-fit: cover;
            border-radius: 5px;
            margin-right: 1rem;
        }

        .pet-card-details {
            flex: 1;
        }

        .score-badge {
            background-color: var(--accent-color);
            color: white;
            padding: 0.3rem 0.6rem;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            margin-left: 0.5rem;
        }

        /* Slider and input styling */
        .stSlider {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        .stSlider > div > div > div {
            background-color: var(--primary-color) !important;
        }

        .stButton > button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: background-color 0.3s ease;
        }

        .stButton > button:hover {
            background-color: var(--secondary-color);
        }

        /* Section styling */
        .section-container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            padding: 1.5rem;
            margin-bottom: 2rem;
        }

        .section-title {
            color: var(--primary-color);
            font-size: 1.5rem;
            margin-bottom: 1rem;
            border-bottom: 1px solid var(--light-gray);
            padding-bottom: 0.5rem;
        }

        /* Footer styling */
        .footer {
            text-align: center;
            padding: 1rem 0;
            border-top: 1px solid var(--light-gray);
            margin-top: 2rem;
            color: #666;
        }

        /* Chart styling */
        .chart-container {
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            .pet-card-content {
                flex-direction: column;
            }

            .pet-card-image {
                width: 100%;
                margin-right: 0;
                margin-bottom: 1rem;
            }
        }
    </style>
    """, unsafe_allow_html=True)


# Sample pet data
def load_pet_data():
    pets = {
        "pets": [
            {
                "id": 1,
                "name": "Golden Retriever",
                "type": "Dog",
                "image": "https://images.unsplash.com/photo-1586671267731-da2cf3ceeb80?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "description": "Friendly, intelligent, and devoted. Golden Retrievers are excellent family dogs that require moderate exercise.",
                "attributes": {
                    "space_required": 0.8,  # 0-1 scale (1 = high)
                    "activity_level": 0.7,
                    "time_commitment": 0.8,
                    "cost": 0.7,
                    "allergy_friendly": 0.2,
                    "noise_level": 0.5,
                    "child_friendly": 0.9,
                    "trainability": 0.9,
                    "lifespan": 0.6  # 10-12 years normalized
                }
            },
            {
                "id": 2,
                "name": "Siamese Cat",
                "type": "Cat",
                "image": "https://images.unsplash.com/photo-1555685812-4b8f594e8e3b?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "description": "Vocal, intelligent, and social. Siamese cats form strong bonds with their owners and are more dog-like in their attachment.",
                "attributes": {
                    "space_required": 0.4,
                    "activity_level": 0.5,
                    "time_commitment": 0.5,
                    "cost": 0.5,
                    "allergy_friendly": 0.3,
                    "noise_level": 0.7,
                    "child_friendly": 0.7,
                    "trainability": 0.7,
                    "lifespan": 0.8  # 12-15 years normalized
                }
            },
            {
                "id": 3,
                "name": "Budgerigar (Budgie)",
                "type": "Bird",
                "image": "https://images.unsplash.com/photo-1591198936750-16d8e998e7c5?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "description": "Small, colorful, and social birds. Budgies are playful and can learn to mimic words and sounds.",
                "attributes": {
                    "space_required": 0.2,
                    "activity_level": 0.6,
                    "time_commitment": 0.5,
                    "cost": 0.3,
                    "allergy_friendly": 0.4,
                    "noise_level": 0.6,
                    "child_friendly": 0.6,
                    "trainability": 0.6,
                    "lifespan": 0.5  # 5-8 years normalized
                }
            },
            {
                "id": 4,
                "name": "Holland Lop Rabbit",
                "type": "Rabbit",
                "image": "https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "description": "Gentle, calm, and affectionate. Holland Lops are popular pets due to their small size and friendly temperament.",
                "attributes": {
                    "space_required": 0.4,
                    "activity_level": 0.5,
                    "time_commitment": 0.6,
                    "cost": 0.4,
                    "allergy_friendly": 0.5,
                    "noise_level": 0.1,
                    "child_friendly": 0.7,
                    "trainability": 0.5,
                    "lifespan": 0.5  # 7-10 years normalized
                }
            },
            {
                "id": 5,
                "name": "Beagle",
                "type": "Dog",
                "image": "https://images.unsplash.com/photo-1505628346881-b72b27e84530?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "description": "Curious, merry, and friendly. Beagles are scent hounds with high energy levels and a strong hunting instinct.",
                "attributes": {
                    "space_required": 0.6,
                    "activity_level": 0.8,
                    "time_commitment": 0.7,
                    "cost": 0.6,
                    "allergy_friendly": 0.3,
                    "noise_level": 0.8,
                    "child_friendly": 0.9,
                    "trainability": 0.5,
                    "lifespan": 0.7  # 12-15 years normalized
                }
            },
            {
                "id": 6,
                "name": "Maine Coon Cat",
                "type": "Cat",
                "image": "https://images.unsplash.com/photo-1596854407944-02f20dc9d8ee?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "description": "Gentle, friendly, and intelligent. Maine Coons are one of the largest domestic cat breeds and are known for their sociable nature.",
                "attributes": {
                    "space_required": 0.5,
                    "activity_level": 0.6,
                    "time_commitment": 0.5,
                    "cost": 0.7,
                    "allergy_friendly": 0.2,
                    "noise_level": 0.3,
                    "child_friendly": 0.8,
                    "trainability": 0.6,
                    "lifespan": 0.7  # 12-15 years normalized
                }
            },
            {
                "id": 7,
                "name": "Syrian Hamster",
                "type": "Small Pet",
                "image": "https://images.unsplash.com/photo-1425082661705-1834bfd09dca?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "description": "Solitary, nocturnal, and easy to care for. Syrian hamsters are popular beginner pets that require minimal space.",
                "attributes": {
                    "space_required": 0.1,
                    "activity_level": 0.6,
                    "time_commitment": 0.3,
                    "cost": 0.2,
                    "allergy_friendly": 0.6,
                    "noise_level": 0.2,
                    "child_friendly": 0.5,
                    "trainability": 0.2,
                    "lifespan": 0.2  # 2-3 years normalized
                }
            },
            {
                "id": 8,
                "name": "African Grey Parrot",
                "type": "Bird",
                "image": "https://images.unsplash.com/photo-1522858547137-f98ab027aeb0?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "description": "Highly intelligent and excellent talkers. African Grey Parrots require significant mental stimulation and social interaction.",
                "attributes": {
                    "space_required": 0.5,
                    "activity_level": 0.7,
                    "time_commitment": 0.9,
                    "cost": 0.9,
                    "allergy_friendly": 0.3,
                    "noise_level": 0.7,
                    "child_friendly": 0.5,
                    "trainability": 0.9,
                    "lifespan": 1.0  # 40-60 years normalized
                }
            },
            {
                "id": 9,
                "name": "Betta Fish",
                "type": "Fish",
                "image": "https://images.unsplash.com/photo-1545048702-79362797cd2d?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "description": "Colorful, solitary fish with distinctive flowing fins. Bettas are relatively easy to care for but require proper water conditions.",
                "attributes": {
                    "space_required": 0.1,
                    "activity_level": 0.2,
                    "time_commitment": 0.2,
                    "cost": 0.2,
                    "allergy_friendly": 1.0,
                    "noise_level": 0.0,
                    "child_friendly": 0.4,
                    "trainability": 0.1,
                    "lifespan": 0.3  # 3-5 years normalized
                }
            },
            {
                "id": 10,
                "name": "Labrador Retriever",
                "type": "Dog",
                "image": "https://images.unsplash.com/photo-1591769225440-811ad7d6eab2?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "description": "Outgoing, even-tempered, and athletic. Labradors are versatile family dogs that excel in many roles from therapy to search and rescue.",
                "attributes": {
                    "space_required": 0.7,
                    "activity_level": 0.8,
                    "time_commitment": 0.8,
                    "cost": 0.7,
                    "allergy_friendly": 0.2,
                    "noise_level": 0.5,
                    "child_friendly": 1.0,
                    "trainability": 0.9,
                    "lifespan": 0.7  # 10-14 years normalized
                }
            }
        ]
    }
    return pets


# Function to calculate weighted scores using WSM
def calculate_pet_scores(pets_data, user_weights):
    scored_pets = []

    for pet in pets_data["pets"]:
        score = 0
        pet_attributes = pet["attributes"]

        # Calculate the weighted sum
        for criterion, weight in user_weights.items():
            if criterion in pet_attributes:
                # For criteria where lower is better (like cost), invert the score
                if criterion in ["cost", "noise_level"]:
                    score += (1 - pet_attributes[criterion]) * weight
                else:
                    score += pet_attributes[criterion] * weight

        # Normalize score to a 0-100 scale
        max_possible_score = sum(user_weights.values())
        normalized_score = (score / max_possible_score) * 100 if max_possible_score > 0 else 0

        # Add the score to the pet data
        pet_with_score = pet.copy()
        pet_with_score["score"] = normalized_score
        scored_pets.append(pet_with_score)

    # Sort pets by score in descending order
    scored_pets.sort(key=lambda x: x["score"], reverse=True)
    return scored_pets


# Function to display pet recommendation cards
def display_pet_card(pet, rank):
    with st.container():
        st.markdown(f"""
        <div class="pet-card">
            <h3>{rank}. {pet['name']} <span class="score-badge">{pet['score']:.1f}%</span></h3>
            <div class="pet-card-content">
                <img src="{pet['image']}" class="pet-card-image" alt="{pet['name']}">
                <div class="pet-card-details">
                    <p><strong>Type:</strong> {pet['type']}</p>
                    <p>{pet['description']}</p>
                    <p><strong>Key Attributes:</strong></p>
                    <ul>
                        <li>Space Required: {'High' if pet['attributes']['space_required'] > 0.6 else 'Medium' if pet['attributes']['space_required'] > 0.3 else 'Low'}</li>
                        <li>Activity Level: {'High' if pet['attributes']['activity_level'] > 0.6 else 'Medium' if pet['attributes']['activity_level'] > 0.3 else 'Low'}</li>
                        <li>Time Commitment: {'High' if pet['attributes']['time_commitment'] > 0.6 else 'Medium' if pet['attributes']['time_commitment'] > 0.3 else 'Low'}</li>
                        <li>Cost: {'High' if pet['attributes']['cost'] > 0.6 else 'Medium' if pet['attributes']['cost'] > 0.3 else 'Low'}</li>
                    </ul>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# Function to create a radar chart for pet attributes
def create_radar_chart(pet):
    # Prepare data for radar chart
    attributes = list(pet["attributes"].keys())
    values = list(pet["attributes"].values())

    # Number of variables
    N = len(attributes)

    # What will be the angle of each axis in the plot
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Close the loop

    # Values need to be repeated to close the loop
    values += values[:1]

    # Initialize the figure
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # Draw one axis per variable and add labels
    plt.xticks(angles[:-1], attributes, color='grey', size=10)

    # Draw the outline of the chart
    ax.plot(angles, values, linewidth=2, linestyle='solid', color='#4e89ae')

    # Fill area
    ax.fill(angles, values, alpha=0.25, color='#4e89ae')

    # Set y-limits
    ax.set_ylim(0, 1)

    # Add title
    plt.title(f"Attribute Profile: {pet['name']}", size=15, color='#4e89ae', y=1.1)

    return fig


# Main application
def main():
    # Apply custom CSS
    local_css()

    # Application header
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="app-header">🐾 Pet Selection Advisor</h1>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Introduction
    st.markdown("""
    <div class="section-container">
        <h2 class="section-title">Find Your Perfect Pet Companion</h2>
        <p>Welcome to the Pet Selection Advisor! This tool will help you find the perfect pet for your lifestyle and preferences. 
        Simply adjust the importance of each criterion below, and we'll recommend pets that match your needs.</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for user inputs
    st.sidebar.markdown('<h2 style="color: #4e89ae;">Your Preferences</h2>', unsafe_allow_html=True)
    st.sidebar.markdown('Adjust the sliders to indicate how important each factor is to you:')

    # User preference inputs
    user_weights = {}

    user_weights["space_required"] = st.sidebar.slider(
        "Available Space",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="How important is the amount of space the pet requires? Higher value means you prioritize pets that need less space."
    )

    user_weights["activity_level"] = st.sidebar.slider(
        "Activity Level",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="How important is the pet's activity level? Higher value means you prefer more active pets."
    )

    user_weights["time_commitment"] = st.sidebar.slider(
        "Time Available",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="How important is the amount of time required for pet care? Higher value means you have more time available."
    )

    user_weights["cost"] = st.sidebar.slider(
        "Budget Consideration",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="How important is the cost of keeping the pet? Higher value means cost is a significant factor."
    )

    user_weights["allergy_friendly"] = st.sidebar.slider(
        "Allergy Concerns",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="How important is it that the pet is allergy-friendly? Higher value means you need a hypoallergenic pet."
    )

    user_weights["noise_level"] = st.sidebar.slider(
        "Noise Sensitivity",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.1,
        help="How important is the pet's noise level? Higher value means you prefer quieter pets."
    )

    user_weights["child_friendly"] = st.sidebar.slider(
        "Child Friendliness",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="How important is it that the pet is good with children? Higher value means you prioritize child-friendly pets."
    )

    user_weights["trainability"] = st.sidebar.slider(
        "Trainability",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="How important is it that the pet is easy to train? Higher value means you prefer highly trainable pets."
    )

    user_weights["lifespan"] = st.sidebar.slider(
        "Lifespan",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="How important is the pet's lifespan? Higher value means you prefer pets with longer lifespans."
    )

    # Additional filters
    st.sidebar.markdown('<h3 style="color: #4e89ae;">Additional Filters</h3>', unsafe_allow_html=True)

    pet_types = ["All Types", "Dog", "Cat", "Bird", "Fish", "Small Pet", "Rabbit"]
    selected_type = st.sidebar.selectbox("Pet Type", pet_types)

    # Load pet data
    pets_data = load_pet_data()

    # Filter by pet type if not "All Types"
    if selected_type != "All Types":
        filtered_pets = {"pets": [pet for pet in pets_data["pets"] if pet["type"] == selected_type]}
    else:
        filtered_pets = pets_data

    # Calculate scores
    scored_pets = calculate_pet_scores(filtered_pets, user_weights)

    # Find your match button
    if st.sidebar.button("Find Your Perfect Pet Match"):
        st.session_state.results_ready = True

    # Display results
    if 'results_ready' in st.session_state and st.session_state.results_ready:
        # Display top recommendations
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">Your Top Pet Recommendations</h2>', unsafe_allow_html=True)

        if len(scored_pets) > 0:
            # Display top 3 pets
            top_pets = scored_pets[:3]

            # Create columns for top 3
            cols = st.columns(3)

            for i, (col, pet) in enumerate(zip(cols, top_pets)):
                with col:
                    st.image(pet["image"], caption=f"{i + 1}. {pet['name']}", use_column_width=True)
                    st.markdown(
                        f"<h3 style='text-align: center;'>{pet['name']} <span class='score-badge'>{pet['score']:.1f}%</span></h3>",
                        unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center;'><strong>Type:</strong> {pet['type']}</p>",
                                unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # Detailed results
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            st.markdown('<h2 class="section-title">Detailed Results</h2>', unsafe_allow_html=True)

            # Show detailed cards for all recommended pets
            for i, pet in enumerate(scored_pets):
                display_pet_card(pet, i + 1)

                # Add a "View Details" expander for each pet
                with st.expander(f"View Detailed Analysis for {pet['name']}"):
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        st.markdown(f"### {pet['name']} Profile")
                        st.markdown(f"**Description:** {pet['description']}")

                        # Create a table of attributes
                        attributes_df = pd.DataFrame({
                            'Attribute': list(pet['attributes'].keys()),
                            'Value': list(pet['attributes'].values())
                        })

                        # Format the values as percentages
                        attributes_df['Value'] = attributes_df['Value'].apply(lambda x: f"{x * 100:.0f}%")

                        # Display the table
                        st.table(attributes_df)

                    with col2:
                        # Display radar chart
                        radar_fig = create_radar_chart(pet)
                        st.pyplot(radar_fig)

            st.markdown('</div>', unsafe_allow_html=True)

            # Comparison chart for top pets
            st.markdown('<div class="section-container">', unsafe_allow_html=True)
            st.markdown('<h2 class="section-title">Compare Top Recommendations</h2>', unsafe_allow_html=True)

            # Prepare data for comparison chart
            compare_data = []
            for pet in top_pets:
                for attr, value in pet["attributes"].items():
                    compare_data.append({
                        "Pet": pet["name"],
                        "Attribute": attr.replace("_", " ").title(),
                        "Value": value
                    })

            df_compare = pd.DataFrame(compare_data)

            # Create a grouped bar chart using Altair
            chart = alt.Chart(df_compare).mark_bar().encode(
                x=alt.X('Pet:N', title='Pet'),
                y=alt.Y('Value:Q', title='Score (0-1)', scale=alt.Scale(domain=[0, 1])),
                color=alt.Color('Pet:N', legend=alt.Legend(title="Pet")),
                column=alt.Column('Attribute:N', title=None)
            ).properties(
                width=90,
                height=200
            ).configure_view(
                stroke=None
            )

            st.altair_chart(chart, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No pets found matching your criteria. Please adjust your preferences.")
    else:
        # Show some general information about choosing a pet
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">How It Works</h2>', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("""
            1. **Set Your Preferences**: Use the sliders on the left to indicate how important each factor is to you.
            2. **Apply Filters**: Optionally filter by pet type if you have specific preferences.
            3. **Find Your Match**: Click the button to see your personalized recommendations.
            4. **Explore Options**: Review detailed information about each recommended pet.
            """)

        with col2:
            st.markdown("""
            The Pet Selection Advisor uses a multi-criteria decision-making approach called the Weighted Sum Method (WSM) to match you with pets that best fit your lifestyle and preferences.

            Each pet in our database is scored on various attributes, and these scores are weighted according to your indicated preferences to find the best matches.
            """)

        st.markdown('</div>', unsafe_allow_html=True)

        # Tips for pet ownership
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="section-title">Tips for Responsible Pet Ownership</h2>', unsafe_allow_html=True)

        st.markdown("""
        - **Research thoroughly** before bringing a pet home
        - **Consider adoption** from local shelters
        - **Budget for all expenses** including unexpected veterinary care
        - **Ensure you have adequate time** to spend with your pet
        - **Prepare your home** for the specific needs of your chosen pet
        - **Commit to the entire lifespan** of the pet you choose
        """)

        st.markdown('</div>', unsafe_allow_html=True)

        # Footer
        st.markdown("""
        <div class="footer">
            <p>Pet Selection Advisor • Decision Support System • 2025</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    # Khởi tạo session state nếu chưa có
    if 'results_ready' not in st.session_state:
        st.session_state.results_ready = False
    main()  # Gọi hàm chính
