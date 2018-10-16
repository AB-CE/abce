.. role:: py(code)
    :language: python


Tutorial for Plant Modeling
===========================

1. Lets write the 1st agent:

    a. Create a file chpplant.py import abcEconomics and create a Plant class.

       .. code:: python

           import abcEconomics


           class CHPPlant(abcEconomics.Agent, abcEconomics.Firm):


    #. In :py:`def init(self):` (not __init__!) we need to create some initial goods

       .. code:: python

            class CHPPlant(...):

                ...
                def init(self):
                    self.create('biogas', 100)
                    self.create('water', 100)

    #. Now we need to specify production functions. There are standard production functions like cobb-douglas and leontief already implemented, but our plants get more complicated production functions.
       We define the production function a firm uses in :py:`def init(self)`.
       So there add the following lines, :py:`class CHPPLant(...):`

       .. code:: python

            class CHPPlant(...):

                def init(self):
                    self.create('biogas', 100)
                    self.create('water', 100)

                    def production_function(biogas, water):
                        electricity = biogas ** 0.25 * water ** 0.5
                        steam = min(biogas, water)
                        biogas = 0
                        water = 0
                        return locals()

                    self.production_function = production_function

     The :py:`def production_function(biogas, water):` returns the production result as a dictionary. (try :py:`print(production_function(10, 10))`). Each key is a good that is produced or what remains of a good after the production process. If goods are used up they must be set to 0. For example the function above creates electricity and steam. Electricity is produced by a cobb-douglas production function. While steam is the minimum between the amount of water and fuel used.

     The :py:`production_function` function is local function in the :py:`init` method.  Make sure the :py:`return locals()` is part of the :py:`def production_function(...):` not of the :py:`def init(self):` method.

    #. In order to produce create a production method in :py:`class CHPPlant(...):` insert the following code right after the :py:`def init(self):` method:

       .. code:: python

           class CHPPlant(...):
                ...
                def production(self):
                    self.produce(self.production_function, {'biogas': 100, 'water': 100})

    e. also add:

       .. code:: python

           class CHPPlant(...):
                ...
                def refill(self):
                    self.create('biogas', 100)
                    self.create('water', 100)

3. Create a file :code:`start.py` to run this incomplete simulation.

    a. Import abcEconomics and the plant:

        .. code:: python

            import abcEconomics
            from chpplant import CHPPlant

    #. Create a simulation instance:

        .. code:: python

            simulation = abcEconomics.Simulation()

    #. Build an a plant

         .. code:: python

            chpplant = simulation.build_agents(CHPPlant, 'chpplant', number=1)

       With this we create 1 agent of type CHPPLANT, it's group name will be :py:`chpplant` and its number :py:`0`.
       Therefore its name is the tuple ('chpplant', 0)

     #. Loop over the simulation:

        .. code:: python

            for r in range(100):
                simulation.advance_round(r)
                chpplant.production()
                chpplant.panel_log(goods=['electricity', 'biogas', 'water', 'steam'], variables=[])
                chpplant.refill()

            simulation.graphs()
            simulation.finalize()



       This will tell the simulation that in every round, the plant execute the :py:`production` method we specified in CHPPLant. Then it refills the input goods. Lastly, it creates a snapshot of the goods of chpplant as will be specified in (e).

       simulation.advance_round(r) sets the time r. Lastly **:py:`simulation.graphs()`** or :py:`simulation.finalize()` tells the simulation that the loop is done. Otherwise the program hangs at the end.

 4. To run your simulation, the best is to use the terminal and in the directory of your simulation type :code:`python start.py`. In SPYDER make sure that BEFORE you run the simulation for the first time you modify the ‘Run Setting’ and choose ‘Execute in external System Terminal’. If you the simulation in the IDE without making this changes the GUI might block.

5. Lets modify the agent so he is ready for trade


    a. now delete the refill function in CHPPlant, both in the agent and in the actionlist delete :py:`chpplant.refill()`

    #. let's simplify the production method in CHPPlant to

       .. code:: python

           def production(self):
               self.produce_use_everything()

    #. in :py:`init` we create money with :py:`self.create('money', 1000)`

7. Now let's create a second agent ADPlant.


    a. copy chpplant.py to applant.py and

    #. in adplant.py change the class name to ADPlant

    #. ADPlant will produce biogas and water out of steam and electricity. In order to achieve this forget about thermodynamics and change the production function to

       .. code:: python

            def production_function(steam, electricity):
                biogas = min(electricity, steam)
                water = min(electricity, steam)
                electricity = 0
                steam = 0
                return locals()

    #. Given the new technology, we need to feed different goods into our machines. Replace the production step

       .. code:: python


        def production(self):
            self.produce(self.production_function, {'steam': self['steam'], 'electricity': self['electricity']})

       self['steam'], looks up the amount of steam the company owns. self.not_reserved['steam'], would look up
       the amount of steam a company owns minus all steam that is offered to be sold to a different company.

    #. ADPlant will sell everything it produces to CHPPlant. We know that the group name of chpplant is 'chpplant and its id number (id) is 0. Add another method to the ADPlant class.

       .. code:: python

           def selling(self):
               amount_biogas = self['biogas]
               amount_water = self['water']
               self.sell(('chpplant', 0), good='water', quantity=amount_water, price=1)
               self.sell(('chpplant', 0), good='biogas', quantity=amount_biogas, price=1)

       This makes a sell offer to chpplant.

    #. In CHPPlant respond to this offer, by adding the following method.

       .. code:: python

            def buying(self):
                water_offer = self.get_offers('water')[0]
                biogas_offer = self.get_offers('biogas')[0]

                if (water_offer.price * water_offer.quantity +
                        biogas_offer.price * biogas_offer.quantity < self['money']):
                    self.accept(water_offer)
                    self.accept(biogas_offer)
                else:
                    quantity_allocationg_half_my_money = self['money'] / water_offer.price
                    self.accept(water_offer, min(water_offer.quantity, quantity_allocationg_half_my_money))
                    self.accept(biogas_offer, min(biogas_offer, self['money']))

       This accepts both offers if it can afford it, if the plant can't, it allocates half of the money for either good.

    #. reversely in CHPPlant:

       .. code:: python

           def selling(self):
               amount_electricity = self['electricity']
               amount_steam = self['steam']
               self.sell(('adplant', 0), good='electricity', quantity=amount_electricity, price=1)
               self.sell(('adplant', 0), good='steam', quantity=amount_steam, price=1)

    #. and in ADPlant:

       .. code:: python

            def buying(self):
                el_offer = self.get_offers('electricity')[0]
                steam_offer = self.get_offers('steam')[0]

                if (el_offer.price * el_offer.quantity
                    + steam_offer.price * steam_offer.quantity < self['money']):
                    self.accept(el_offer)
                    self.accept(steam_offer)
                else:
                    quantity_allocationg_half_my_money = self['money'] / el_offer.price
                    self.accept(el_offer, min(el_offer.quantity, quantity_allocationg_half_my_money))
                    self.accept(steam_offer, min(steam_offer, self['money']))


8. let's modify start.py

    b. in :code:`start.py` import thu ADPlant:

       .. code:: python

           from adplant import ADPlant

       and

       .. code:: python

          adplant = simulation.build_agents(ADPlant, 'adplant', number=1)

    c. change the action list to:

       .. code:: python


           for r in range(100):
               simulation.advance_round(r)
               (chpplant + adplant).production()
               (chpplant + adplant).selling()
               (chpplant + adplant).buying()
               chpplant.panel()

9. now it should run again.
