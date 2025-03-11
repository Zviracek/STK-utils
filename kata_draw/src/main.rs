// Prevent console window in addition to Slint window in Windows release builds when, e.g., starting the app via file manager. Ignored on other platforms.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use rand::prelude::SliceRandom;
use std::error::Error;

use rand::thread_rng;
use std::io;

use slint::{ModelRc, SharedString, VecModel};

slint::include_modules!();

const MIN_PAIRS: i32 = 4;
const MAX_PAIRS: i32 = 25;
const MAX_PER_GROUP: i32 = 5;
const MAX_GROUPS: i32 = MAX_PAIRS / MAX_PER_GROUP;
const MIN_ROUNDS: i32 = 2;
const MAX_ROUNDS: i32 = 5;

fn main() -> Result<(), Box<dyn Error>> {
    //let num_of_pairs = get_number_in_range("Number of pairs:", MIN_PAIRS, MAX_PAIRS);
    //let num_of_rounds = get_number_in_range("Number of rounds:", MIN_ROUNDS, MAX_ROUNDS);
    //
    //let num_of_groups = get_number_of_groups(num_of_pairs);
    //let pairs = distribute_pairs(num_of_pairs, num_of_groups);
    //
    //println!("Distribution: {:?}", pairs);
    //println!();
    //
    //for i in 0..num_of_rounds {
    //    let dist = populate_round(num_of_pairs, num_of_groups);
    //    println!("Round {}:", i + 1);
    //    for (j, group) in dist.iter().enumerate() {
    //        if *group == [0; MAX_GROUPS as usize] {
    //            break;
    //        }
    //        println!("Group {}: {:?}", j + 1, group);
    //    }
    //    println!();
    //}
    //
    //let mut input = String::new();
    //
    //println!("Press Enter to exit...");
    //let _ = io::stdin().read_line(&mut input);

    let ui = AppWindow::new()?;

    ui.on_generate({
        let ui_handle = ui.as_weak();
        move || {
            let ui = ui_handle.unwrap();
            //ui.set_counter(ui.get_counter() + 1);
            let num_of_pairs_str = ui.get_inputed_pairs().to_string();
            let num_of_rounds_str = ui.get_inputed_rounds().to_string();

            //println!("{}", num_of_pairs_str);
            if num_of_pairs_str.is_empty() || num_of_rounds_str.is_empty() {
            } else {
                let mut num_of_pairs = num_of_pairs_str.parse::<i32>().unwrap();
                let mut num_of_rounds = num_of_rounds_str.parse::<i32>().unwrap();

                num_of_pairs = num_of_pairs.clamp(MIN_PAIRS, MAX_PAIRS);
                num_of_rounds = num_of_rounds.clamp(MIN_ROUNDS, MAX_ROUNDS);

                //println!("{}", num_of_pairs);
                let num_of_groups = get_number_of_groups(num_of_pairs);
                let pairs = distribute_pairs(num_of_pairs, num_of_groups);
                let mut data =
                    [[[0; MAX_PER_GROUP as usize]; MAX_GROUPS as usize]; MAX_ROUNDS as usize];
                for i in 0..num_of_rounds as usize {
                    data[i] = populate_round(num_of_pairs, num_of_groups);
                }

                let data_vec: Vec<_> = data
                    .iter()
                    .map(|table_layer| {
                        let rows: Vec<_> = table_layer
                            .iter()
                            .map(|row| ModelRc::new(VecModel::from(row.to_vec())))
                            .collect();
                        ModelRc::new(VecModel::from(rows))
                    })
                    .collect();

                ui.set_data(ModelRc::new(VecModel::from(data_vec)));

                ui.set_groups(num_of_groups);
                ui.set_rounds(num_of_rounds);
                ui.set_inputed_pairs(SharedString::from(num_of_pairs.to_string()));
                ui.set_inputed_rounds(SharedString::from(num_of_rounds.to_string()));
            }
        }
    });

    ui.run()?;

    Ok(())
}

fn get_number_of_groups(pairs: i32) -> i32 {
    let mut groups = (pairs + MAX_PER_GROUP - 1) / MAX_PER_GROUP; // Integer division rounded up
    if groups == 1 {
        groups = 2; // Even though they would fit, least number of groups is always two
    }

    groups
}

fn distribute_pairs(pairs: i32, groups: i32) -> [i32; MAX_GROUPS as usize] {
    let mut pairs_in_groups = [0; MAX_GROUPS as usize];
    let mut remaining_pairs = pairs;
    for i in 0..groups as usize {
        pairs_in_groups[i] = pairs / groups;
        remaining_pairs -= pairs / groups;
    }

    for i in 0..groups as usize {
        if remaining_pairs > 0 {
            pairs_in_groups[i] += 1;
            remaining_pairs -= 1;
        }
    }

    pairs_in_groups
}

fn populate_round(
    num_of_pairs: i32,
    num_of_groups: i32,
) -> [[i32; MAX_PER_GROUP as usize]; MAX_GROUPS as usize] {
    let mut pairs = vec![];
    for i in 1..num_of_pairs + 1 {
        pairs.push(i);
    }
    pairs.shuffle(&mut thread_rng());
    let mut dist = [[0; MAX_PER_GROUP as usize]; MAX_GROUPS as usize];

    let mut j: i32 = 0;
    let mut last_added_index = 0;
    // Take all of the shuffled pairs and insert them round robin into Distribution
    // i is index into shuffled, j is index into group number and last_added_index points to
    // position inside group
    for pair in pairs {
        dist[j as usize][last_added_index] = pair;
        j += 1;
        if j == num_of_groups {
            j = 0;
            last_added_index += 1;
        }
    }

    dist
}

fn get_number_in_range(prompt: &str, min: i32, max: i32) -> i32 {
    loop {
        println!("{}", prompt);
        let mut input = String::new();

        io::stdin()
            .read_line(&mut input)
            .expect("Failed to read input");

        match input.trim().parse::<i32>() {
            Ok(num) if num >= min && num <= max => return num,
            Ok(_) => println!("Number must be between {} and {}", min, max),
            Err(_) => println!("Invalid input. Please enter a valid integer."),
        }
        println!();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_distribution() {
        let cases = vec![
            (4, [2, 2, 0, 0, 0]),
            (5, [3, 2, 0, 0, 0]),
            (7, [4, 3, 0, 0, 0]),
            (11, [4, 4, 3, 0, 0]),
            (16, [4, 4, 4, 4, 0]),
            (19, [5, 5, 5, 4, 0]),
            (21, [5, 4, 4, 4, 4]),
            (25, [5, 5, 5, 5, 5]),
        ];

        for (input, expected) in cases {
            let groups = get_number_of_groups(input);
            assert_eq!(
                distribute_pairs(input, groups),
                expected,
                "Distribution failed on {} pairs",
                input
            )
        }
    }
}
