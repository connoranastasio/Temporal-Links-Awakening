import os
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecVideoRecorder
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.monitor import Monitor
from env.link_env import LinkEnv

def make_env():
    env = LinkEnv(render=True)  # ✅ Now supports video
    env = Monitor(env)
    return env

def main():
    os.makedirs("videos", exist_ok=True)
    os.makedirs("checkpoints", exist_ok=True)

    # Create environment with video recording
    env = DummyVecEnv([make_env])
    env = VecVideoRecorder(env, video_folder="videos", record_video_trigger=lambda x: x % 10_000 == 0,
                           video_length=1000, name_prefix="ppo_episode")

    # Initialize PPO
    model = PPO(
        "CnnPolicy",
        env,
        verbose=1,
        tensorboard_log="./tensorboard_logs"
    )

    # Save checkpoints
    checkpoint_callback = CheckpointCallback(
        save_freq=10_000,
        save_path="./checkpoints",
        name_prefix="ppo_linksawakening"
    )

    # Train
    model.learn(
        total_timesteps=1_000_000,
        callback=checkpoint_callback
    )

    # Save final model
    model.save("ppo_linksawakening_final")

    # Evaluation
    eval_env = DummyVecEnv([make_env])
    mean_reward, std_reward = evaluate_policy(model, eval_env, n_eval_episodes=5, render=False)
    print(f"Evaluation over 5 episodes: mean_reward={mean_reward:.2f} ± {std_reward:.2f}")

    # Close environments
    env.close()
    eval_env.close()

if __name__ == "__main__":
    main()
