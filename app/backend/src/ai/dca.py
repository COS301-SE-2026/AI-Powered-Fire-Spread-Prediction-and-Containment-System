from pytorchfire import WildfireModel

model = WildfireModel() # creates a model with default params and environment data
model = model.cuda() # move model to gpu

for _ in range(100): # runs model for 100 steps
    model.compute()

    # reference is the study done for pytorch by MIT this is just a base modal is gonna be modified to not use the other variables but to use the ignition from the xgboost