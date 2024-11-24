import matplotlib.pyplot as plt
import numpy as np
import random

# Constants and Parameters

# Customer Acquisition Costs (CAC)
driver_cac_low = 400
driver_cac_high = 600
rider_cac_low = 10
rider_cac_high = 20

# Initial Numbers
initial_drivers = 5
initial_riders = 500

# Time Frame
months = 12

# Driver Parameters
driver_avg_rides_per_month = 100
driver_churn_rate = 0.05  # 5% monthly churn
driver_first_month_tier = 3  # Start at Tier 3 for one month
driver_first_months = 1      # Number of months to keep initial tier

# Revised Driver Tiers
driver_tiers = {
    1: {'rides_required': 100, 'earning_multiplier': 1.00, 'points_per_ride': 0.525},
    2: {'rides_required': 250, 'earning_multiplier': 1.02, 'points_per_ride': 0.65},
    3: {'rides_required': 400, 'earning_multiplier': 1.04, 'points_per_ride': 0.75},
    4: {'rides_required': 600, 'earning_multiplier': 1.06, 'points_per_ride': 0.90},
    5: {'rides_required': 850, 'earning_multiplier': 1.08, 'points_per_ride': 1.20},
    6: {'rides_required': 1100, 'earning_multiplier': 1.10, 'points_per_ride': 1.50},
}

# Revised Rider Tiers
rider_tiers = {
    1: {'rides_required': 30, 'discount': 0.015, 'monthly_voucher': 5.00, 'points_per_ride': 1},
    2: {'rides_required': 80, 'discount': 0.020, 'monthly_voucher': 7.50, 'points_per_ride': 1.1},
    3: {'rides_required': 150, 'discount': 0.025, 'monthly_voucher': 10.00, 'points_per_ride': 1.2},
    4: {'rides_required': 250, 'discount': 0.030, 'monthly_voucher': 12.50, 'points_per_ride': 1.3},
    5: {'rides_required': 400, 'discount': 0.035, 'monthly_voucher': 15.00, 'points_per_ride': 1.5},
    6: {'rides_required': 600, 'discount': 0.040, 'monthly_voucher': 20.00, 'points_per_ride': 1.75},
    7: {'rides_required': 800, 'discount': 0.050, 'monthly_voucher': 25.00, 'points_per_ride': 2},
}

# Pricing
base_ride_price = 25.00
base_driver_pay = 19.00

# Incentive Caps
driver_earning_cap = 1.10  # Maximum of 10% above base pay per month
rider_min_payment = 22.00  # Rider payments do not drop below $22 per ride

# Classes for Driver and Rider

class Driver:
    def __init__(self, join_month):
        self.join_month = join_month
        self.total_rides = 0
        self.months_active = 0
        self.active = True
        self.points = 0  # Points accumulated
        self.initial_tier_months = driver_first_months
        self.current_tier = driver_first_month_tier  # Start at Tier 3 for initial promotion

    def update_tier(self):
        # After initial promotion months, update tier based on total_rides
        if self.initial_tier_months > 0:
            self.initial_tier_months -= 1
        else:
            for tier_level in sorted(driver_tiers.keys(), reverse=True):
                if self.total_rides >= driver_tiers[tier_level]['rides_required']:
                    self.current_tier = tier_level
                    break
            else:
                self.current_tier = 1

    def simulate_month(self):
        if not self.active:
            return 0
        self.months_active += 1
        rides_this_month = driver_avg_rides_per_month
        self.total_rides += rides_this_month
        # Earn points
        points_earned = driver_tiers[self.current_tier]['points_per_ride'] * rides_this_month
        self.points += points_earned
        # Churn check
        if random.random() < driver_churn_rate:
            self.active = False
        return rides_this_month

class Rider:
    def __init__(self, join_month):
        self.join_month = join_month
        self.total_rides = 0
        self.current_tier = 1
        self.months_active = 0
        self.active = True
        self.points = 0  # Points accumulated

    def update_tier(self):
        for tier_level in sorted(rider_tiers.keys(), reverse=True):
            if self.total_rides >= rider_tiers[tier_level]['rides_required']:
                self.current_tier = tier_level
                break
            else:
                self.current_tier = 1

    def simulate_month(self, match_rate):
        if not self.active:
            return 0, False  # No rides, no failed match
        self.months_active += 1
        rides_requested = rider_avg_rides_per_month
        rides_completed = 0
        failed_match = False
        for _ in range(int(rides_requested)):
            if random.random() < match_rate:
                rides_completed += 1
            else:
                failed_match = True
        self.total_rides += rides_completed
        # Earn points
        points_earned = rider_tiers[self.current_tier]['points_per_ride'] * rides_completed
        self.points += points_earned
        # Churn check
        churn_rate = rider_churn_rate_fail if failed_match else rider_churn_rate_no_fail
        if random.random() < churn_rate:
            self.active = False
        return rides_completed, failed_match

# Simulation

def simulate(high_cac=True):
    # Initialize lists for drivers and riders
    drivers = [Driver(join_month=0) for _ in range(initial_drivers)]
    riders = [Rider(join_month=0) for _ in range(initial_riders)]
    
    # Net revenue tracking
    net_revenues = []
    cumulative_net_revenue = 0

    # Data for graphs
    driver_counts = []
    driver_tier_counts = {tier: [] for tier in driver_tiers.keys()}
    rider_counts = []
    rider_tier_counts = {tier: [] for tier in rider_tiers.keys()}
    driver_tier_payouts = {tier: [] for tier in driver_tiers.keys()}
    rider_tier_revenues = {tier: [] for tier in rider_tiers.keys()}
    
    # CAC based on high or low scenario
    driver_cac = driver_cac_high if high_cac else driver_cac_low
    rider_cac = rider_cac_high if high_cac else rider_cac_low

    # Marketing Budget (Assuming fixed for simplicity)
    marketing_budget_per_month = 10000
    driver_marketing_allocation = 0.5  # 50% of budget to drivers
    rider_marketing_allocation = 0.5   # 50% of budget to riders

    for month in range(1, months + 1):
        # Acquire new drivers and riders
        driver_marketing_spend = marketing_budget_per_month * driver_marketing_allocation
        rider_marketing_spend = marketing_budget_per_month * rider_marketing_allocation

        new_drivers = int(driver_marketing_spend / driver_cac)
        new_riders = int(rider_marketing_spend / rider_cac)

        drivers.extend([Driver(join_month=month) for _ in range(new_drivers)])
        riders.extend([Rider(join_month=month) for _ in range(new_riders)])

        # Initialize revenue and payout entries for this month
        for tier in driver_tiers.keys():
            driver_tier_payouts[tier].append(0)
        for tier in rider_tiers.keys():
            rider_tier_revenues[tier].append(0)

        # Simulate driver activity
        active_drivers = [driver for driver in drivers if driver.active]
        driver_tier_distribution = {tier: 0 for tier in driver_tiers.keys()}
        for driver in active_drivers:
            driver.simulate_month()
            driver_tier_distribution[driver.current_tier] += 1

        # Calculate match rate based on driver availability
        match_rate = min(0.6 + (len(active_drivers) / (initial_drivers + month * new_drivers)) * 0.4, 0.93)

        # Simulate rider activity
        total_rides = 0
        total_failed_matches = 0
        active_riders = [rider for rider in riders if rider.active]
        rider_tier_distribution = {tier: 0 for tier in rider_tiers.keys()}
        for rider in active_riders:
            rides_completed, failed_match = rider.simulate_month(match_rate)
            total_rides += rides_completed
            if failed_match:
                total_failed_matches += 1
            rider_tier_distribution[rider.current_tier] += 1

        # Calculate net revenue
        net_revenue = 0
        total_driver_payouts = 0
        total_rider_revenues = 0

        for ride in range(int(total_rides)):
            # Select a random rider and driver from active ones
            rider = random.choice(active_riders)
            driver = random.choice(active_drivers)
            
            # Update tiers
            rider.update_tier()
            driver.update_tier()

            # Rider's payment
            discount = rider_tiers[rider.current_tier]['discount']
            rider_payment = base_ride_price * (1 - discount)
            # Apply rider incentive cap
            rider_payment = max(rider_payment, rider_min_payment)
            # Rider points redemption
            points_to_redeem = int(rider.points // 20) * 20  # Every 20 points can be redeemed
            rider_points_value = (points_to_redeem / 20) * 1.00  # $1 per 20 points
            rider.points -= points_to_redeem
            rider_payment -= rider_points_value
            rider_payment = max(rider_payment, rider_min_payment)
            total_rider_revenues += rider_payment
            rider_tier_revenues[rider.current_tier][-1] += rider_payment

            # Driver's earnings
            earning_multiplier = driver_tiers[driver.current_tier]['earning_multiplier']
            driver_pay = base_driver_pay * earning_multiplier
            # Apply driver incentive cap
            max_driver_pay = base_driver_pay * driver_earning_cap
            driver_pay = min(driver_pay, max_driver_pay)
            # Driver points redemption
            driver_points_value = driver.points * 0.50  # $0.50 per point
            driver.points = 0  # Reset points after redemption
            driver_pay += driver_points_value
            total_driver_payouts += driver_pay
            driver_tier_payouts[driver.current_tier][-1] += driver_pay

        # Net revenue for the month
        net_revenue = total_rider_revenues - total_driver_payouts
        cumulative_net_revenue += net_revenue
        net_revenues.append(cumulative_net_revenue)

        # Collect data for graphs
        driver_counts.append(len(active_drivers))
        for tier in driver_tiers.keys():
            driver_tier_counts[tier].append(driver_tier_distribution[tier])

        rider_counts.append(len(active_riders))
        for tier in rider_tiers.keys():
            rider_tier_counts[tier].append(rider_tier_distribution[tier])

        print(f"Month {month}:")
        print(f"  Active Drivers: {len(active_drivers)}")
        print(f"  Active Riders: {len(active_riders)}")
        print(f"  Total Rides Completed: {total_rides}")
        print(f"  Total Failed Matches: {total_failed_matches}")
        print(f"  Net Revenue This Month: ${net_revenue:.2f}")
        print(f"  Cumulative Net Revenue: ${cumulative_net_revenue:.2f}\n")

    # Return all collected data
    return {
        'net_revenues': net_revenues,
        'driver_counts': driver_counts,
        'driver_tier_counts': driver_tier_counts,
        'driver_tier_payouts': driver_tier_payouts,
        'rider_counts': rider_counts,
        'rider_tier_counts': rider_tier_counts,
        'rider_tier_revenues': rider_tier_revenues,
    }

# Run Simulation (choose high or low CAC scenario)
print("Simulating Low CAC Scenario with Adjusted Incentives:\n")
simulation_data = simulate(high_cac=False)

# Extract data for plotting
months_range = np.arange(1, months + 1)
net_revenues = simulation_data['net_revenues']
driver_counts = simulation_data['driver_counts']
driver_tier_counts = simulation_data['driver_tier_counts']
driver_tier_payouts = simulation_data['driver_tier_payouts']
rider_counts = simulation_data['rider_counts']
rider_tier_counts = simulation_data['rider_tier_counts']
rider_tier_revenues = simulation_data['rider_tier_revenues']

# Plotting Cumulative Net Revenue Over 12 Months
plt.figure(figsize=(12, 6))
plt.plot(months_range, net_revenues, marker='o')
plt.xlabel('Months')
plt.ylabel('Cumulative Net Revenue ($)')
plt.title('Cumulative Net Revenue Over 12 Months')
plt.grid(True)
plt.show()

# Plotting Total Number of Drivers per Month
plt.figure(figsize=(12, 6))
plt.plot(months_range, driver_counts, marker='o')
plt.xlabel('Months')
plt.ylabel('Number of Active Drivers')
plt.title('Total Active Drivers Over 12 Months')
plt.grid(True)
plt.show()

# Plotting Breakdown of Drivers by Tier
plt.figure(figsize=(12, 6))
for tier in sorted(driver_tiers.keys()):
    plt.plot(months_range, driver_tier_counts[tier], label=f'Tier {tier}')
plt.xlabel('Months')
plt.ylabel('Number of Drivers')
plt.title('Driver Distribution by Tier Over 12 Months')
plt.legend()
plt.grid(True)
plt.show()

# Plotting Total Number of Riders per Month
plt.figure(figsize=(12, 6))
plt.plot(months_range, rider_counts, marker='o')
plt.xlabel('Months')
plt.ylabel('Number of Active Riders')
plt.title('Total Active Riders Over 12 Months')
plt.grid(True)
plt.show()

# Plotting Breakdown of Riders by Tier
plt.figure(figsize=(12, 6))
for tier in sorted(rider_tiers.keys()):
    plt.plot(months_range, rider_tier_counts[tier], label=f'Tier {tier}')
plt.xlabel('Months')
plt.ylabel('Number of Riders')
plt.title('Rider Distribution by Tier Over 12 Months')
plt.legend()
plt.grid(True)
plt.show()

# Plotting Driver Payouts by Tier Over 12 Months
plt.figure(figsize=(12, 6))
for tier in sorted(driver_tiers.keys()):
    payouts = driver_tier_payouts[tier]
    plt.plot(months_range, payouts, label=f'Tier {tier}')
plt.xlabel('Months')
plt.ylabel('Driver Payouts ($)')
plt.title('Driver Payouts by Tier Over 12 Months')
plt.legend()
plt.grid(True)
plt.show()

# Plotting Revenue from Riders by Tier Over 12 Months
plt.figure(figsize=(12, 6))
for tier in sorted(rider_tiers.keys()):
    revenues = rider_tier_revenues[tier]
    plt.plot(months_range, revenues, label=f'Tier {tier}')
plt.xlabel('Months')
plt.ylabel('Revenue from Riders ($)')
plt.title('Revenue from Riders by Tier Over 12 Months')
plt.legend()
plt.grid(True)
plt.show()
