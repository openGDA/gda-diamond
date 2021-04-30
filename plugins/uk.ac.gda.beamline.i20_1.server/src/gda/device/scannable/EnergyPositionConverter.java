package gda.device.scannable;

import java.util.Arrays;
import java.util.List;

import javax.measure.Quantity;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import gda.device.DeviceException;
import gda.scan.TurboXasMotorParameters;
import gda.util.QuantityFactory;
import gda.util.converters.IQuantityConverter;

/**
 * Convert between energy and position using motor parameters from {@link TurboXasScannable}.
 * i.e. {@link TurboXasMotorParameters#getPositionForEnergy(double)} and {@link TurboXasMotorParameters#getEnergyForPosition(double)}
 *
 * @param <S>
 * @param <T>
 */
public class EnergyPositionConverter <S extends Quantity<S>, T extends Quantity<T>> implements IQuantityConverter<S, T> {
	private static final Logger logger = LoggerFactory.getLogger(EnergyPositionConverter.class);

	private static final String MOTOR_UNITS = "mm";
	private static final String ENERGY_UNITS = "eV";

	private TurboXasScannable turboXasScannable;

	public void setTurboXasScannable(TurboXasScannable turboXasScannable) {
		this.turboXasScannable = turboXasScannable;
	}

	/**
	 * Convert from motor position (mm) to energy (eV)
	 */
	@Override
	public Quantity<S> toSource(Quantity<T> target) throws Exception {
		double pos = target.getValue().doubleValue();
		logger.debug("Trying to convert motor position {} to energy", pos);
		TurboXasMotorParameters params = getMotorParams();
		if (params == null) {
			return QuantityFactory.createFromObject(pos, ENERGY_UNITS);
		}
		return QuantityFactory.createFromObject(params.getEnergyForPosition(pos), ENERGY_UNITS);
	}

	/**
	 * Convert from energy (eV) to motor position (mm)
	 */
	@Override
	public Quantity<T> toTarget(Quantity<S> source) throws Exception {
		double energy = source.getValue().doubleValue();
		logger.debug("Trying to convert energy {} to position", energy);
		TurboXasMotorParameters params = getMotorParams();
		if (params == null) {
			return QuantityFactory.createFromObject(energy, MOTOR_UNITS);
		}
		try {
			return QuantityFactory.createFromObject(params.getPositionForEnergy(energy), MOTOR_UNITS);
		} catch(IllegalArgumentException e) {
			throw new DeviceException(e);
		}
	}

	@Override
	public boolean sourceMinIsTargetMax() {
		return true;
	}

	@Override
	public List<String> getAcceptableSourceUnits() {
		return Arrays.asList(ENERGY_UNITS);
	}

	@Override
	public List<String> getAcceptableTargetUnits() {
		return Arrays.asList(MOTOR_UNITS);
	}

	@Override
	public boolean handlesStoT() {
		return true;
	}

	@Override
	public boolean handlesTtoS() {
		return true;
	}

	private TurboXasMotorParameters getMotorParams() throws DeviceException {
		TurboXasMotorParameters params = turboXasScannable.getMotorParameters();
		if (params == null) {
			logger.warn("Cannot convert between energy and position - no motor parameters have been set on "+turboXasScannable.getName());
		}
		return params;
	}
}