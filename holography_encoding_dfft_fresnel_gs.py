import numpy as np
import matplotlib.pyplot as plt
from scipy import fft
from PIL import Image
import os

# 设置全局参数（SLM适配）
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def gerchberg_saxton_fourier(target_amplitude, wavelength, focal_length, pixel_size, iterations=50):
    """
    基于GS迭代算法生成傅里叶变换全息图
    :param target_amplitude: 目标振幅图像
    :param wavelength: 波长
    :param focal_length: 焦距
    :param pixel_size: 像素尺寸
    :param iterations: 迭代次数
    :return: 频谱相位全息图, 重建振幅图像
    """
    height, width = target_amplitude.shape
    phase = np.random.uniform(0, 2 * np.pi, (height, width))  # 初始相位
    k = 2 * np.pi / wavelength  # 波数

    # 迭代优化
    for i in range(iterations):
        complex_field = target_amplitude * np.exp(1j * phase)

        # DFFT传播
        hologram_spectrum = fft.fft2(complex_field)
        hologram_phase = np.angle(hologram_spectrum)

        reconstructed_field = fft.ifft2(np.exp(1j * hologram_phase))
        phase = np.angle(reconstructed_field)

        if (i + 1) % 10 == 0:
            mse = np.mean((np.abs(reconstructed_field) - target_amplitude) ** 2)
            print(f"迭代 {i + 1}/{iterations}, 均方误差: {mse:.6f}")

    return hologram_phase, np.abs(reconstructed_field)


def save_spectrum_phase_hologram(phase_data, file_path):
    """
    保存频谱相位全息图（灰度PNG）
    :param phase_data: 频谱相位数据
    :param file_path: 保存路径
    """
    # 相位值归一化到0~255
    phase_normalized = (phase_data - np.min(phase_data)) / (np.max(phase_data) - np.min(phase_data))
    phase_8bit = (phase_normalized * 255).astype(np.uint8)

    # 创建无装饰的灰度图
    plt.figure(figsize=(phase_data.shape[1] / 100, phase_data.shape[0] / 100), dpi=100)
    plt.imshow(phase_8bit, cmap='gray')
    plt.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # 无损保存PNG
    plt.savefig(file_path, format='png', bbox_inches='tight', pad_inches=0, dpi=100)
    plt.close()

    print(f"频谱相位全息图已保存至: {os.path.abspath(file_path)}")
    print(f"相位范围: [{np.min(phase_data):.2f}, {np.max(phase_data):.2f}] → 灰度范围: [0, 255]")


def visualize_results(target, hologram_phase, reconstruction):
    """
    可视化目标图像、频谱相位全息图和重建图像
    :param target: 目标振幅图像
    :param hologram_phase: 频谱相位全息图
    :param reconstruction: 重建振幅图像
    """
    plt.figure(figsize=(20, 8))

    plt.subplot(131)
    plt.title('目标振幅')
    plt.imshow(target, cmap='gray')
    plt.axis('off')

    plt.subplot(132)
    plt.title('频谱相位全息图（HSV可视化）')
    plt.imshow(hologram_phase, cmap='hsv')
    plt.axis('off')

    plt.subplot(133)
    plt.title('重建振幅')
    plt.imshow(reconstruction, cmap='gray')
    plt.axis('off')

    plt.tight_layout()
    plt.show()


def main():
    # 物理参数
    width, height = 1920, 1080  # 1080p分辨率
    focal_length = 0.2  # 焦距20cm
    wavelength = 671e-9  # 波长671nm
    pixel_size = 8e-6  # SLM像素尺寸
    imaging_focal_length = 0.25  # 成像焦距25cm

    # 读取目标文件
    try:
        img = Image.open("light_1080p.png").convert('L')
        target_array = np.array(img, dtype=np.float32)

        # 校验尺寸
        if target_array.shape != (height, width):
            raise ValueError(f"图片尺寸不符！需1080x1920，实际为{target_array.shape}")

        # 对比度拉伸
        non_zero = target_array[target_array > 0]
        if len(non_zero) == 0:
            raise ValueError("图片全黑，无法处理")

        min_val = np.min(non_zero)
        max_val = np.max(target_array)

        target_amplitude = (target_array - min_val) / (max_val - min_val)
        target_amplitude = np.clip(target_amplitude, 0, 1)

    except FileNotFoundError:
        print("错误：未找到'light_1080p.png'文件，请确保图片在当前目录下")
        return
    except Exception as e:
        print(f"错误：读取图片时发生异常 - {e}")
        return

    # 计算频谱相位全息图
    hologram_phase, reconstruction = gerchberg_saxton_fourier(
        target_amplitude, wavelength=wavelength, focal_length=focal_length, pixel_size=pixel_size, iterations=100
    )

    # 增强重建图像亮度
    reconstruction = np.clip(reconstruction * 1.2, 0, 1)

    # 可视化结果
    visualize_results(target_amplitude, hologram_phase, reconstruction)

    # 保存频谱相位全息图
    output_path = './results/spectrum_phase_hologram_1080p.png'  # 输出路径
    save_spectrum_phase_hologram(hologram_phase, output_path)

if __name__ == "__main__":
    main()