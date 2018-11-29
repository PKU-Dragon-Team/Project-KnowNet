def compute_error(b, m, data):

    totalError = 0
    # Two ways to implement this
    # first way
    for i, _ in enumerate(data):
        x = data[i][0]
        y = data[i][1]
        totalError += (y-(m*x+b))**2

    # second way
    # x = data[:,0]
    # y = data[:,1]
    # totalError = (y-m*x-b)**2
    # totalError = np.sum(totalError,axis=0)

    return totalError/float(len(data))


def optimizer(data, starting_b, starting_m, learning_rate, num_iter):
    b = starting_b
    m = starting_m

    # gradient descent
    for _ in range(num_iter):
        # update b and m with the new more accurate b and m by performing
        # the gradient step
        b, m = compute_gradient(b, m, data, learning_rate)
    return [b, m]


def compute_gradient(b_current, m_current, data, learning_rate):

    b_gradient = 0
    m_gradient = 0

    N = float(len(data))

    for i, _ in enumerate(data):
        x = data[i][0]
        y = data[i][1]

        b_gradient += -(2/N) * (y-((m_current*x)+b_current))
        m_gradient += -(2/N) * x * (y-((m_current*x)+b_current))

    new_b = b_current - (learning_rate * b_gradient)
    new_m = m_current - (learning_rate * m_gradient)
    return [new_b, new_m]


def linear_regression(data):
    # get train data
    # data =np.array(data)

    # define hyperparamters
    # learning_rate is used for update gradient
    # define the number that will iteration
    # define y =mx+b
    learning_rate = 0.01
    initial_b = 0.0
    initial_m = 0.0
    num_iter = 10000

    # train model
    return optimizer(data, initial_b, initial_m, learning_rate, num_iter)
