
import random

reviews = [
    {
        'review_subject_line': "Best Product EVER",
        'review_contents': "It slices is dices. It's a hair tonic, floor cleaner, a dessert topping and more. I bought this because I needed to put a new roof on the garage. Boy, was I surprised when after receiving the self-opening package it installed itself!!!!! My neighbors came over right away and said, 'how do you get it done so fast?' I told him a story about how I'm friends with Santa and he let me sub-contract some Christmas Elves.  The neighbor bought it."
    },
    {
        'review_subject_line': "Came Damaged and Can't Get a Refund",
        'review_contents': "I bought this using a personal 3rd party check made out to cash countersigned by the national bank of Antarctica.  The shipping took forever as they company appears to save freight costs by grind up the item using a woodchipper and using the powder that comes out as cushioning material in mattresses. I received it on Thursday and followed the assembly instructions religiously.  The company was kind enough to supply excellent instructions and a 55-gallon barrel of glue. After assembly I tried to get some music out of it but not a peep. What is the world coming to when they make cinder block holders so cheap?"
    },
    {
        'review_subject_line': "I would give it 12 stars, but I couldn't get it to eat sadness",
        'review_contents': "We bought this because we just bought a new house with a basement full of sadness and thought this would eat the sadness and turn it into cash. Instead, we got something that eats angst and makes tomatoed paste. It wasn't an unhappy ending as we found a friend with teenagers, and he was more than willing to trade us for a Japanese beetle collection."
    },    
    {
        'review_subject_line': "Try Putting This in Your Eye!",
        'review_contents': "Doctor recommended putting this in my eye to cure my near sightedness.  Worked for the first few hours then began to see colors i had never seen before.  Solved the problem by wearing this under a pair of sunglasses. 5 Stars."
    },    
    {
        'review_subject_line': "A Gift From My Boss",
        'review_contents': "Garry, my boss, gave this to me as a thank you for all my hard works!!!"
    },
    {
        'review_subject_line': "A little to heavy for my taste",
        'review_contents': "I'm a hang glider junky and when I strap this to my rig it really plays havic with my GPS system. I think it has to do with the way gravity works. When I don't have this with me I can fly from my house in death valley to work easily with only short stops to drink water. I would recommend this to anyone that commutes to work on the ground."
    },
    {
        'review_subject_line': "Had to replace the battery with a roll of life-saver to make this work",
        'review_contents': "Power for this thing is insane! Needed to up my game so we use Wintergreen life-savers now."
    },
    {
        'review_subject_line': "The Description Was Wrong",
        'review_contents': "We found that you couldn't create world pools by using the power of your mind with this.  Very sad."
    },
    {
        'review_subject_line': "Completely Useful",
        'review_contents': "I don't know what the problem is with some people. When I put this under my pillow I sleep like a baby."
    },
    {
        'review_subject_line': "Love the horn",
        'review_contents': "The horn on this thing is awesome."
    },
    {
        'review_subject_line': "Found one of these buried in my backyard",
        'review_contents': "I think I might need to call someone to dig up the rest of the yard."
    },
    {
        'review_subject_line': "Kids use it for soccer practice",
        'review_contents': "This is as tall as it is wide which makes it perfect for soccer. Thank you so much"
    },

]

subject_objects = [
    {'subject' : 'crab',
     'imgs' : [
         'E1-crab.jpeg',
         'E2-crab.jpeg',
         'E3-crab.jpeg'
        ],
     'reviews' : reviews
    },
    {'subject' : 'screws',
     'imgs' : [
         'B1-screws.jpeg',
         'B2-screws.jpeg',
         'B3-screws.jpeg'
        ],
     'reviews' : reviews
    },
    {'subject' : 'duck',
     'imgs' : [
         'D1-duck.jpeg',
         'D2-duck.jpeg',
         'D3-duck.jpeg'
        ],
     'reviews' : reviews
    },
    {'subject' : 'bass',
     'imgs' : [
         'C1-bass.jpeg',
         'C2-bass.jpeg',
         'C3-bass.jpeg'
        ],
     'reviews' : reviews
    },
    {'subject' : 'cloud',
     'imgs' : [
         'A1-cloud.jpeg',
         'A2-cloud.jpeg',
         'A3-cloud.jpeg'
        ]
        ,
     'reviews' : reviews
    }
]


def make_slide(subject, img, active=False):
    active_str = ""
    if active:
        active_str = "active"

    slide_temp = f"""
        <div class="carousel-item {active_str}" data-bs-interval="4000">
            <img src="{img}" class="d-block w-100" alt="{subject}">
        </div>
    """
    return slide_temp

def make_carousels(subject_object):
    slides = ""
    first = True
    subject = subject_object['subject']
    img_list = subject_object['imgs']
    for img in img_list:
        img = f'images/{img}'
        slides += make_slide(subject, img, active=first)
        first = False

    car_temp = f"""
        <div id="carousel-{subject}-review" class="carousel slide" data-bs-ride="carousel">
        <div class="carousel-inner">
            {slides}
        </div>
        <button class="carousel-control-prev" type="button" data-bs-target="#carousel-{subject}-review" data-bs-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Previous</span>
        </button>
        <button class="carousel-control-next" type="button" data-bs-target="#carousel-{subject}-review" data-bs-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Next</span>
        </button>
        </div>

    """
    return car_temp


def make_accordian(subject, review_subject_line, review_contents, number, expanded, show):
    accord_temp = f"""
                                        <div class="accordion-item">
                                            <h2 class="accordion-header" id="panelsStayOpen-heading-{subject}-{number}">
                                                <button class="accordion-button bg-gray text-white" type="button" data-bs-toggle="collapse" data-bs-target="#panelsStayOpen-{subject}-{number}" aria-expanded="{expanded}" aria-controls="panelsStayOpen-collapseOne">
                                                {review_subject_line}
                                                </button>
                                            </h2>
                                            <div id="panelsStayOpen-{subject}-{number}" class="accordion-collapse collapse {show}" aria-labelledby="panelsStayOpen-heading-{subject}">
                                                <div class="accordion-body bg-gray-dif">
                                                {review_contents}
                                                </div>
                                            </div>    
                                        </div>
    """
    return accord_temp

def make_accordians(subject_object):
    all_str = ""
    subject = subject_object['subject']
    reviews = subject_object['reviews']
    all_str += f'<div class="accordion accordion-flush" id="accordionPanels-{subject}">'
    random.shuffle(reviews)
    first = 'true'
    show = 'show'
    for i, review in enumerate(reviews):
        review_subject_line = review['review_subject_line']
        review_contents = review['review_contents']
        all_str += make_accordian(subject, review_subject_line, review_contents, i, first, show)
        first = 'false'
        show = ''
    all_str += f'</div>\n'
    return all_str

def make_reviews(subject_object):
    carousels = make_carousels(subject_object)
    accordians = make_accordians(subject_object)
    subject = subject_object['subject']

    review_temp = f"""
                <div class="reviews-screen"> 
                    <div class="row">
                        <div class="col-6">
                            <h3>User Images</h3>
                        </div>
                        <div class="col-6">
                            <h3>Rank</h3>
                        </div>
                    </div>
                    <div class="row">
                            <div class="col-6">

                                    {carousels}

                            </div>

                            <div class="col-6 d-flex align-items-center justify-content-center">
                                    <svg class="bar" id="{subject}-bars"></svg>
                            </div>
                    </div>

                    <div class="row">
                        <div class="col mt-3">

                                    {accordians}

                        </div>
                    </div>
                </div>
    """
    return review_temp


def make_review_divs(subject_objects):
    for so in subject_objects:
        subject = so['subject']
        review_panel = make_reviews(so)
        with open(f'../public/{subject}-review.html', 'w') as ofh:
            ofh.write(review_panel)


if __name__ == "__main__":
    make_review_divs(subject_objects)
