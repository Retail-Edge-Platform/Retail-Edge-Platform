#!/usr/bin/env python3

import random
import time
from weighteddice import roll



class Session(object):
    """Session represents a single session of interaction

    An Example session might look like this 
        Pickup: Product 1
        Display: Product 1 Page
        Send: pick-up Event for Product 1

        Touch: Product 1 Reviews Button
        Show: Product 1 Reviews
        Send: Touch Event for Product 1, Reviews Button

        Touch: Product 1 Video Button
        Show: Product 1 Video and Play
        Send: Touch Event for Product 1, Video Button

        Put down: Product 1
        Send: put-down Event for Product 1

        Pickup: Product 2
        Display: Product 2 Page
        Send: pick-up Event for Product 2

        Touch: Product 2 Video Button
        Show: Product 2 Video and Play
        Send: Touch Event for Product 2, Video Button

        Put down: Product 2
        Send: put-down Event for Product 2

    Attributes
    ----------
    ST_PICKUP : str
        Tag for pick up event
    ST_REVIEW : str
        Tag for looking at review event
    ST_VIDEO : str
        Tag for looking at video event
    ST_PUTDOWN : str
        Tag for the put the product back down event
    """

    ST_PICKUP = "pick-up"  # Is the start
    ST_REVIEW = "touch-review"  # REVIEW, VIDEO are selected or not
    ST_VIDEO = "touch-video"
    ST_PUTDOWN = "put-down" # 

    def __init__ ( self, start_of_sesssion_time, number_of_products):
        """Initialize a session that will start at
        *start_of_sesssion_time* (in millisecond since the epoch) and
        will have the option of picking from *number_of_products*.
        
        Note: There are multiple instances in this code were PDFs have
        been chosen that might not best reflect the actual 
        interactions to be modeled. There has been an attempt to record 
        those that have been recognized as TODOs.

        ```python
        # time now (ms since epoch)
        start_of_sesssion_time = time.time() * 1000
        # Number of product chosen out of thin air for this example
        number_of_products = 15

        session = Session(start_of_sesssion_time, number_of_products)
        print(session.get_session())
        # Should print something like
        # (1623509321230,
        #     [{"product": 12, "timestamp": 1623509294471, "event": "PICKUP"},
        #      {"product": 12, "timestamp":  1623509321230, "event": "PUTDOWN"},
        #      ...]
        # )
        ```
        """
        self.session_events = []
        self.start_of_sesssion_time = start_of_sesssion_time
        self.number_of_products = number_of_products
        
    def _get_interaction_plan(self):
        self.i_plan = []
        # Add an interaction state and a delta time place holder
        self.i_plan.append([self.ST_PICKUP, 0])
        # Customer could ask for more info multiple times
        info_rounds = random.randrange(1,3)
        for _ in range(info_rounds):
            # Next we have multiple choices around getting more information
            # Expect these biases to change based on customer and length of session
            # For expample if reviews aren't helpful or customer is in a hurry
            # TODO: Add variability based on data collected (backlog)
            more_info_bias_list = (0.30, 0.60, 0.10) # Review, Video, Not_curious
            more_info_outcome = roll(more_info_bias_list)
            if more_info_outcome == 1:
                self.i_plan.append([self.ST_REVIEW, 0])
            elif more_info_outcome == 2:
                self.i_plan.append([self.ST_VIDEO, 0])
            elif more_info_outcome == 3:
                pass # Not curious
            else:
                # How did I get here? Added another choice and need to write
                # another elif. So, for now print warning (could be throw exception)
                # and add another review
                print("WARNING: Need to fix more_info_outcome. Have a choice without an event")
                self.i_plan.append([self.ST_REVIEW,0])
        # Customer now can put it down or put in cart
        # This bias list is also going to change based on the info interaction
        # TODO: Improve putdown/keep model based on info interactions (backlog)
        keep_bias_list = (0.70, 0.30) # Put Back, Keep
        keep_sides = len(keep_bias_list) # add other choices get sides
        keep_outcome = roll(keep_bias_list)
        if keep_outcome == 1:
            self.i_plan.append([self.ST_PUTDOWN, 0])
        elif keep_outcome == 2:
            pass # They keep it and we don't know that 
            # TODO: More complex scenario they pick up two and compare and put only one back (backlog)
            # TODO: They put back not the orginal one that started the interactions (backlog)
        else:
            # How did I get here? Added another choice and need to write
            # another elif. So, for now print warning (could be throw exception)
            # and add another putdown
            print("WARNING: Need to fix keep_outcome. Have a choice without an event")
            self.i_plan.append([self.ST_PUTDOWN, 0])
        # TODO: Change to more realistic distribution based on number of steps (backlog)
        # Time Logic
        # TODO: Better model could be developed (backlog)
        # Most steps from above pickup, info, info, putdown
        # if one step zero seconds always
        if len(self.i_plan) == 1:
            # Least steps from above they pickup and keep it == one steps
            # no time calc needed
            total_delta_time = 0  # Pick it up and go 
            return self.i_plan, total_delta_time 
        else:
            # if two steps 5 seconds min and 30 seconds max (pickup and anything)
            # if three steps 10 seconds min and 30 seconds max 
            # if four steps 15 seconds min and 30 seconds max
            min_time = (len(self.i_plan) - 1) * 5000
            max_time = 30000
            assert max_time > min_time
            total_delta_time = (random.randrange(min_time, max_time + 1))
            delta_time_ms = total_delta_time / (len(self.i_plan) - 1)
            for i in range(1, len(self.i_plan)):
                # Rounding error will result in final value not always matching
                # total_delta_time
                self.i_plan[i][1] = i * delta_time_ms # Rounding will mean error 
            return self.i_plan, total_delta_time
        
    def get_session(self):
        # Calc an upper bound on the session
        # needs to be greater than 5 seconds and less than 180 seconds
        session_time_soft_upper_bounds = (180 - 30) * 1000 # (ms) should allow max to be 180 seconds
        # TODO: After python 3.2 this should produce more equally distributed values.
        #       This is most likely not representative of the distribution we are sampling from reality.
        #       Study actual data to determine more approraite distribution and apply here (backlog)
        session_time = random.randrange(5000, session_time_soft_upper_bounds + 1) + self.start_of_sesssion_time
        session_time_total = self.start_of_sesssion_time
        session_plan = []
        # Create a selection list 
        # Assume that during a session a product will only be selected once
        # Random sampling without replacement
        # TODO: Again this is not representative of anything real fix after looking at real data (backlog)
        products_list = list(range(1,self.number_of_products + 1))

        while session_time_total < session_time:
            # Pick a product TODO: Uniform where as this will not be uniform (backlog)
            product_number = random.sample(products_list, 1)[0]
            # Plan the interaction
            interaction_plan, interaction_total_delta_time = self._get_interaction_plan()
            # Adjust interaction times
            interaction_plan = [[product_number, event_type, int(delta_time + session_time)] for event_type, delta_time in interaction_plan]
            # Add another interaction to the session
            session_plan.extend(interaction_plan)
            # Accumulate time to session
            session_time_total += interaction_total_delta_time
            # TODO: Pauses between interactions are currently not documented.
            #       Study data a determine approriate distributions to sample from.
            #       Currently using 0.8 to 1.5 seconds (backlog)
            self.session_pause_range = [800, 1500]  # Undefined in spec 
            session_time_total += random.randrange(self.session_pause_range[0], self.session_pause_range[1] + 1)

        # Convert to list of objects
        session_stream = [{"obj_type": "UPDATE", "product-id": product_number, "product-name": f"product-{product_number}", "timestamp": timestamp, "interaction-type": event_type} for product_number, event_type, timestamp in session_plan]

        return session_time_total, session_stream

        
        
if __name__ == "__main__":
    # time now (ms since epoch)
    start_of_sesssion_time = int(time.time() * 1000)
    # Number of product chosen out of thin air for this example
    number_of_products = 15

    session = Session(start_of_sesssion_time, number_of_products)
    print(session.get_session())
    # Should print something like
    # (1623509321230,
    #     [{"product": 12, "timestamp": 1623509294471, "event": "PICKUP"},
    #      {"product": 12, "timestamp":  1623509321230, "event": "PUTDOWN"},
    #      ...]
    # )
 