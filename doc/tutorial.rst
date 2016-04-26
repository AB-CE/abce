.. role:: py(code)
    :language: python


Tutorial for plant modeling
===========================

In this tutorial we will implement an economy that has two plants. These plants have products and by products, products and by products are traded.

1. Prepare the template
    a. Copy start.py household.py and firm.py from the template directory of abce to a new directory (ZIP can be downloaded from here https://github.com/DavoudTaghawiNejad/abce).

    b. rename firm.py to chpplant.py

2. Lets write the 1st agent:

    a. Open chpplant.py change the Firm :py:`class Firm(abce.Agent, abce.Firm):` to :py:`class CHPPlant(abce.Agent, abce.Firm):`

    b. Now we need to specify production functions. There are standard production functions like cobb-douglas and leontief already implemented, but our plants get more complicated production functions.
       We define the production function a firm uses in :py:`def init(self)`. (not __init__ !)                   So there add the following lines, :py:`class CHPPLant(...):`

       .. code:: python

           class Firm(abce.Agent, abce.Firm):
            def init(self, simulation_parameters, agent_parameters):
                def production_function(goods):
                    output = {'electricity': goods['biogas'] ** 0.25 * goods['water'] ** 0.5,
                              'steam': min(goods['biogas'], goods['water'])}
                    return output

                use = {'biogas': 1, 'water': 1}  # inputs that are used for production are consumed completely

                self.set_production_function_many_goods(production_function, use)

     The :py:`def production_function(goods):` returns the production result as a dictionary. Each key is a good that is produced. The value is a formula that sets how the amount of this product is calculated. For example the function above creates electricity and steam. Electricity is produced by a cobb-douglas production function. While steam is the minimum between the amount of water and fuel used.

     :py:`use = {'biogas': 1, 'water': 1}`, specifies how much percent of each good is used up in the process.

     :py:`self.set_production_function(production_function, use)` sets the agents production function to the functions we just created.

    c. in :py:`def init(self):` we need to create some initial goods

       .. code:: python

           ...
           self.create('biogas', 100)
           self.create('water', 100)

    d. In order to produce create a production method in :py:`class CHPPlant(...):` insert the following code right after the :py:`def init(self):` method:

        .. code:: python

            def production(self):
                self.produce({'biogas' : 100, 'water' : 100})

    e. also add:

       .. code:: python

               def refill(self):
                   self.create('biogas', 100)
                   self.create('water', 100)

3. We will now modify start.py to run this incomplete simulation.

    a. replace :py:`from firm import Firm` and :py:`household import Household` with :py:`from chpplant import CHPPLant`. This imports your agent in start.py.

    b. change the :py:`action_list = [...]`. against an action list with only one entry.

       .. code:: python

           action_list = [('chpplant', 'production'),
                          ('chpplant', 'refill'),
                          ('chpplant', 'panel')].

       This will tell the simulation that in every round, the firms execute the :py:`production` method we specified in CHPPLant. Then it refills the input goods. Lastly, it creates a snapshot of the possessions of chpplant as will be specified in (e).

    c. delete :py:`simulation.declare_round_endowment(...)`
       delete :py:`simulation.declare_perishable(...)`
       delete :py:`simulation.build_agents(Household, 'household',...)`

    d. change :py:`simulation.build_agents(Firm, 'firm',...)` to

       .. code:: python

           simulation.build_agents(CHPPlant, 'chpplant ', number=1)

       With this we create 1 agent of type CHPPLANT, it's group name will be :py:`chpplant` and its number :py:`0`.

    e. change:

       .. code:: python

           simulation.panel('household', possessions=['good1', 'good2']
                                         variables=['utility'])

       to:

       .. code:: python

           simulation.panel('chpplant', possessions=['electricity', 'biogas', 'water', 'steam'], variables=[])

 4. To run your simulation, the best is to use the terminal and in the directory of your simulation type :code:`python start.py`. In SPYDER make sure that BEFORE you run the simulation for the first time you modify the ‘Run Setting’ and choose ‘Execute in external System Terminal’. If you the simulation in the IDE without making this changes the GUI might block.

5. Lets modify the agent so he is ready for trade


    a. now delete the refill function in CHPPlant, both in the agent and in the actionlist delete :py:`('chpplant', 'refill'),`

    #. let's simplify the production method in CHPPlant to

       .. code:: python

           def production(self):
               self.produce_use_everything()

    #. in :py:`init` we create money with :py:`self.create('money', 1000)`

7. Now let's create a second agent ADPlant.


    a. copy chpplant.py to applant.py and

    #. in adplant.py change the class name to ADPlant

    #. ADPlant will produce biogas and water out of steam and electricity. In order to achieve this forget about thermodynamics and change:

       .. code:: python

               output = {'electricity': goods['biogas'] ** 0.25 * goods['water'] ** 0.5,
                         'steam': min(goods['biogas'], goods['water'])}
               return output

           use = {'biogas': 1, 'water': 1}  # inputs that are used for production are consumed completely

       to

       .. code:: python

            output = {'biogas':  min(goods['electricity'], goods['steam']),
                      'water': min(goods['electricity'], goods['steam'])}
            return output

        use = {'electricity': 1, 'steam': 1}

    #. ADPlant will sell everything it produces to CHPPlant. We know that the group name of chpplant is 'chpplant and its id number (idn) is 0:

       .. code:: python

           def selling(self):
               amount_biogas = self.possession('biogas')
               amount_water = self.possession('water')
               self.sell('chpplant', 0, good='water', quantity=amount_water, price=1)
               self.sell('chpplant', 0, good='biogas', quantity=amount_biogas, price=1)

       This makes a sell offer to chpplant.

    #. In CHPPlant respond to this offer

       .. code:: python

        def buying(self):
            water_offer = self.get_offers('water')[0]
            biogas_offer = self.get_offers('biogas')[0]

            if (water_offer.price * water_offer.quantity
                + biogas_offer.price * biogas_offer.quantity < self.possession('money')):
                self.accept(water_offer)
                self.accept(biogas_offer)
            else:
                quantity_allocationg_half_my_money = self.possession('money') / water_offer.price
                self.accept(water_offer, min(water_offer.quantity, quantity_allocationg_half_my_money))
                self.accept(biogas_offer, min(biogas_offer, self.possession('money')))

       This accepts both offers if it can afford it, if the plant can't, it allocates half of the money for either good.

    #. reversely in CHPPlant:

       .. code:: python

           def selling(self):
               amount_electricity = self.possession('electricity')
               amount_steam = self.possession('steam')
               self.sell('adplant', 0, good='electricity', quantity=amount_electricity, price=1)
               self.sell('adplant', 0, good='steam', quantity=amount_steam, price=1)

    #. and in ADPlant:

       .. code:: python

            def buying(self):
                el_offer = self.get_offers('electricity')[0]
                steam_offer = self.get_offers('steam')[0]

                if (el_offer.price * el_offer.quantity
                    + steam_offer.price * steam_offer.quantity < self.possession('money')):
                    self.accept(el_offer)
                    self.accept(steam_offer)
                else:
                    quantity_allocationg_half_my_money = self.possession('money') / el_offer.price
                    self.accept(el_offer, min(el_offer.quantity, quantity_allocationg_half_my_money))
                    self.accept(steam_offer, min(steam_offer, self.possession('money')))


8. let's modify start.py

    b. in :code:`start.py` add :py:`from adplant import ADPlant` and :py:`simulation.build_agents(ADPlant, 'adplant', number=1)`

    c. change the action list to:

       .. code:: python

           action_list = [(('chpplant', 'adplant'), 'production'),
                          (('chpplant', 'adplant'), 'selling'),
                          (('chpplant', 'adplant'), 'buying'),
                          ('chpplant', 'panel')]

9. now it should run again.
